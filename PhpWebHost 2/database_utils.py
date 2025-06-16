"""
Database utilities for advanced PostgreSQL operations
"""
import os
import logging
from datetime import datetime, timedelta
from flask import current_app
from models import db, Content, UserInteraction
from sqlalchemy import text, func
import subprocess
import json

class DatabaseManager:
    """Advanced database management utilities"""
    
    @staticmethod
    def create_full_text_search_triggers():
        """Create PostgreSQL triggers for automatic full-text search vector updates"""
        try:
            # Create function to update search vector
            db.session.execute(text("""
                CREATE OR REPLACE FUNCTION update_content_search_vector()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.search_vector := to_tsvector('english', 
                        COALESCE(NEW.title, '') || ' ' || 
                        COALESCE(NEW.content, '') || ' ' ||
                        COALESCE(NEW.tags, '') || ' ' ||
                        COALESCE(NEW.author, '')
                    );
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            # Create trigger
            db.session.execute(text("""
                DROP TRIGGER IF EXISTS content_search_vector_update ON content;
                CREATE TRIGGER content_search_vector_update
                    BEFORE INSERT OR UPDATE ON content
                    FOR EACH ROW EXECUTE FUNCTION update_content_search_vector();
            """))
            
            db.session.commit()
            logging.info("Full-text search triggers created successfully")
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating full-text search triggers: {e}")
            return False
    
    @staticmethod
    def update_all_search_vectors():
        """Update search vectors for all existing content"""
        try:
            db.session.execute(text("""
                UPDATE content SET search_vector = to_tsvector('english', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(content, '') || ' ' ||
                    COALESCE(tags, '') || ' ' ||
                    COALESCE(author, '')
                )
            """))
            db.session.commit()
            logging.info("All search vectors updated successfully")
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating search vectors: {e}")
            return False
    
    @staticmethod
    def full_text_search(query, limit=10):
        """Perform full-text search on content"""
        try:
            search_query = text("""
                SELECT id, title, content, category, author, tags, image, created_at,
                       ts_rank(search_vector, plainto_tsquery('english', :query)) as rank
                FROM content
                WHERE search_vector @@ plainto_tsquery('english', :query)
                  AND status = 'Published'
                ORDER BY rank DESC, created_at DESC
                LIMIT :limit
            """)
            
            result = db.session.execute(search_query, {'query': query, 'limit': limit})
            return result.fetchall()
        except Exception as e:
            logging.error(f"Error in full-text search: {e}")
            return []
    
    @staticmethod
    def create_database_backup(backup_name=None):
        """Create a database backup using pg_dump"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return False, "Database URL not found"
            
            # Extract connection parameters
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            
            backup_command = [
                'pg_dump',
                '-h', parsed.hostname,
                '-p', str(parsed.port),
                '-U', parsed.username,
                '-d', parsed.path[1:],  # Remove leading slash
                '-f', f'/tmp/{backup_name}',
                '--no-password'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password
            
            result = subprocess.run(backup_command, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info(f"Database backup created: {backup_name}")
                return True, backup_name
            else:
                logging.error(f"Backup failed: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logging.error(f"Error creating database backup: {e}")
            return False, str(e)
    
    @staticmethod
    def get_database_statistics():
        """Get comprehensive database statistics"""
        try:
            stats = {}
            
            # Table sizes
            table_sizes = db.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)).fetchall()
            
            stats['table_sizes'] = [dict(row._mapping) for row in table_sizes]
            
            # Index usage
            index_usage = db.session.execute(text("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    indexrelname as indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
            """)).fetchall()
            
            stats['index_usage'] = [dict(row._mapping) for row in index_usage]
            
            # Content statistics
            content_stats = db.session.execute(text("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(LENGTH(content)) as avg_content_length
                FROM content
                GROUP BY status
            """)).fetchall()
            
            stats['content_stats'] = [dict(row._mapping) for row in content_stats]
            
            # Interaction statistics
            interaction_stats = db.session.execute(text("""
                SELECT 
                    interaction_type,
                    COUNT(*) as count,
                    AVG(interaction_score) as avg_score
                FROM user_interactions
                GROUP BY interaction_type
                ORDER BY count DESC
            """)).fetchall()
            
            stats['interaction_stats'] = [dict(row._mapping) for row in interaction_stats]
            
            # Daily activity
            daily_activity = db.session.execute(text("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as interactions
                FROM user_interactions
                WHERE timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """)).fetchall()
            
            stats['daily_activity'] = [dict(row._mapping) for row in daily_activity]
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting database statistics: {e}")
            return {}
    
    @staticmethod
    def optimize_database():
        """Run database optimization commands"""
        try:
            # Analyze tables for query planner
            db.session.execute(text("ANALYZE;"))
            
            # Vacuum tables to reclaim space
            db.session.execute(text("VACUUM;"))
            
            # Reindex for better performance
            db.session.execute(text("REINDEX DATABASE CONCURRENTLY;"))
            
            db.session.commit()
            logging.info("Database optimization completed")
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error optimizing database: {e}")
            return False
    
    @staticmethod
    def cleanup_old_interactions(days=90):
        """Clean up old user interactions to maintain performance"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted = UserInteraction.query.filter(
                UserInteraction.timestamp < cutoff_date
            ).delete()
            
            db.session.commit()
            logging.info(f"Cleaned up {deleted} old interactions")
            return deleted
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error cleaning up old interactions: {e}")
            return 0
    
    @staticmethod
    def create_database_indexes():
        """Create additional performance indexes"""
        try:
            indexes = [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_title_gin ON content USING gin(to_tsvector('english', title));",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_tags_gin ON content USING gin(to_tsvector('english', tags));",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_interactions_user_time ON user_interactions(user_id, timestamp DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_status_created ON content(status, created_at DESC) WHERE status = 'Published';",
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logging.warning(f"Index creation warning: {e}")
            
            logging.info("Additional database indexes created")
            return True
            
        except Exception as e:
            logging.error(f"Error creating database indexes: {e}")
            return False

class DatabaseHealthChecker:
    """Database health monitoring utilities"""
    
    @staticmethod
    def check_connection():
        """Check database connection health"""
        try:
            db.session.execute(text("SELECT 1"))
            return True, "Database connection healthy"
        except Exception as e:
            return False, f"Database connection failed: {e}"
    
    @staticmethod
    def check_table_integrity():
        """Check table integrity and constraints"""
        try:
            issues = []
            
            # Check for orphaned interactions
            orphaned = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM user_interactions ui 
                LEFT JOIN content c ON ui.content_id = c.id 
                WHERE c.id IS NULL
            """)).fetchone()
            
            if orphaned.count > 0:
                issues.append(f"Found {orphaned.count} orphaned user interactions")
            
            # Check for invalid statuses
            invalid_status = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM content 
                WHERE status NOT IN ('Draft', 'Published', 'Archived')
            """)).fetchone()
            
            if invalid_status.count > 0:
                issues.append(f"Found {invalid_status.count} content items with invalid status")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Error checking table integrity: {e}"]
    
    @staticmethod
    def get_performance_metrics():
        """Get database performance metrics"""
        try:
            metrics = {}
            
            # Query performance
            slow_queries = db.session.execute(text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                WHERE mean_time > 100
                ORDER BY mean_time DESC 
                LIMIT 10
            """)).fetchall()
            
            metrics['slow_queries'] = [dict(row._mapping) for row in slow_queries]
            
            # Connection stats
            connections = db.session.execute(text("""
                SELECT 
                    state,
                    COUNT(*) as count
                FROM pg_stat_activity
                GROUP BY state
            """)).fetchall()
            
            metrics['connections'] = [dict(row._mapping) for row in connections]
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error getting performance metrics: {e}")
            return {}