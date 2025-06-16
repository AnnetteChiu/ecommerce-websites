import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, session
from forms import ContentForm, EditContentForm
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import uuid
from models import db, Content, UserInteraction
from database_utils import DatabaseManager, DatabaseHealthChecker
from sqlalchemy import func
import re
from collections import Counter, defaultdict
import numpy as np


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()



# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper functions for file handling
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add UUID to prevent filename conflicts
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None



# Recommendation system functions
def extract_keywords(text, num_keywords=10):
    """Extract important keywords from text content"""
    # Remove HTML tags and special characters
    clean_text = re.sub(r'<[^>]+>', '', text.lower())
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', clean_text)
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'its', 'our', 'their', 'not', 'no', 'yes', 'if', 'when', 'where', 'why', 'how'
    }
    
    # Extract words and count frequency
    words = [word for word in clean_text.split() if len(word) > 3 and word not in stop_words]
    word_freq = Counter(words)
    
    return [word for word, _ in word_freq.most_common(num_keywords)]

def calculate_content_similarity(content1, content2):
    """Calculate similarity between two content items"""
    score = 0
    
    # Category match (high weight)
    if content1.category == content2.category:
        score += 0.4
    
    # Tag overlap (medium weight)
    tags1 = set(content1.get_tags_list())
    tags2 = set(content2.get_tags_list())
    if tags1 and tags2:
        tag_overlap = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
        score += 0.3 * tag_overlap
    
    # Content keyword similarity (medium weight)
    keywords1 = set(extract_keywords(content1.content))
    keywords2 = set(extract_keywords(content2.content))
    if keywords1 and keywords2:
        keyword_overlap = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
        score += 0.2 * keyword_overlap
    
    # Author match (low weight)
    if content1.author == content2.author:
        score += 0.1
    
    return score

def get_content_recommendations(content_id, limit=5):
    """Get recommended content based on similarity to given content"""
    current_content = Content.query.get(content_id)
    if not current_content:
        return []
    
    # Get all other published content
    other_content = Content.query.filter(
        Content.id != content_id,
        Content.status == 'Published'
    ).all()
    
    # Calculate similarity scores
    recommendations = []
    for content in other_content:
        similarity = calculate_content_similarity(current_content, content)
        if similarity > 0:
            recommendations.append({
                'content': content,
                'similarity': similarity,
                'score': similarity
            })
    
    # Sort by similarity and return top recommendations
    recommendations.sort(key=lambda x: x['similarity'], reverse=True)
    return recommendations[:limit]

def get_trending_content(limit=5):
    """Get trending content based on recent creation and tags"""
    # Get recently created content with the most common tags
    recent_content = Content.query.filter(
        Content.status == 'Published'
    ).order_by(Content.created_at.desc()).limit(20).all()
    
    # Count tag frequency
    all_tags = []
    for content in recent_content:
        all_tags.extend(content.get_tags_list())
    
    popular_tags = [tag for tag, _ in Counter(all_tags).most_common(5)]
    
    # Find content with popular tags
    trending = []
    for content in recent_content:
        content_tags = content.get_tags_list()
        tag_score = sum(1 for tag in content_tags if tag in popular_tags)
        if tag_score > 0:
            trending.append({
                'content': content,
                'score': tag_score
            })
    
    trending.sort(key=lambda x: x['score'], reverse=True)
    return trending[:limit]

def get_category_recommendations(category, exclude_id=None, limit=5):
    """Get popular content from the same category"""
    query = Content.query.filter(
        Content.category == category,
        Content.status == 'Published'
    )
    
    if exclude_id:
        query = query.filter(Content.id != exclude_id)
    
    return query.order_by(Content.updated_at.desc()).limit(limit).all()

def get_user_id():
    """Get or create user ID for session tracking"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def track_user_interaction(content_id, interaction_type, score=1.0):
    """Track user interaction for collaborative filtering"""
    try:
        user_id = get_user_id()
        interaction = UserInteraction(
            user_id=user_id,
            content_id=content_id,
            interaction_type=interaction_type,
            interaction_score=score
        )
        db.session.add(interaction)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error tracking interaction: {e}")
        db.session.rollback()

def build_user_item_matrix():
    """Build user-item interaction matrix for collaborative filtering"""
    # Get all interactions from the last 30 days
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    interactions = UserInteraction.query.filter(
        UserInteraction.timestamp >= cutoff_date
    ).all()
    
    # Build user-item matrix
    user_item_matrix = defaultdict(dict)
    users = set()
    items = set()
    
    for interaction in interactions:
        user_item_matrix[interaction.user_id][interaction.content_id] = interaction.interaction_score
        users.add(interaction.user_id)
        items.add(interaction.content_id)
    
    return user_item_matrix, list(users), list(items)

def calculate_user_similarity(user1_items, user2_items):
    """Calculate cosine similarity between two users"""
    # Find common items
    common_items = set(user1_items.keys()) & set(user2_items.keys())
    
    if len(common_items) == 0:
        return 0
    
    # Calculate cosine similarity
    sum_squares1 = sum([user1_items[item] ** 2 for item in user1_items])
    sum_squares2 = sum([user2_items[item] ** 2 for item in user2_items])
    sum_products = sum([user1_items[item] * user2_items[item] for item in common_items])
    
    denominator = (sum_squares1 * sum_squares2) ** 0.5
    if denominator == 0:
        return 0
    
    return sum_products / denominator

def get_collaborative_filtering_recommendations(target_user_id, limit=5):
    """Get recommendations using collaborative filtering"""
    try:
        user_item_matrix, users, items = build_user_item_matrix()
        
        if target_user_id not in user_item_matrix:
            return []
        
        target_user_items = user_item_matrix[target_user_id]
        user_similarities = {}
        
        # Calculate similarity with other users
        for user_id in users:
            if user_id != target_user_id:
                similarity = calculate_user_similarity(target_user_items, user_item_matrix[user_id])
                if similarity > 0:
                    user_similarities[user_id] = similarity
        
        # Get recommendations based on similar users
        recommendations = defaultdict(float)
        total_similarity = sum(user_similarities.values())
        
        if total_similarity == 0:
            return []
        
        for user_id, similarity in user_similarities.items():
            weight = similarity / total_similarity
            for item_id, rating in user_item_matrix[user_id].items():
                if item_id not in target_user_items:  # Don't recommend already interacted items
                    recommendations[item_id] += weight * rating
        
        # Sort and get top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        content_ids = [item_id for item_id, score in sorted_recommendations[:limit]]
        
        # Fetch content objects
        recommended_content = Content.query.filter(
            Content.id.in_(content_ids),
            Content.status == 'Published'
        ).all()
        
        # Return with scores
        result = []
        for content in recommended_content:
            score = next((score for item_id, score in sorted_recommendations if item_id == content.id), 0)
            result.append({
                'content': content,
                'cf_score': round(score, 3)
            })
        
        return result
        
    except Exception as e:
        logging.error(f"Error in collaborative filtering: {e}")
        return []

def get_hybrid_recommendations(content_id, limit=5):
    """Get hybrid recommendations combining content-based and collaborative filtering"""
    try:
        user_id = get_user_id()
        
        # Get content-based recommendations (existing function)
        content_based = get_content_recommendations(content_id, limit=limit//2 + 1)
        
        # Get collaborative filtering recommendations
        cf_based = get_collaborative_filtering_recommendations(user_id, limit=limit//2 + 1)
        
        # Combine and deduplicate
        all_recommendations = {}
        
        # Add content-based with weight
        for rec in content_based:
            all_recommendations[rec['content'].id] = {
                'content': rec['content'],
                'content_score': rec['similarity'],
                'cf_score': 0,
                'hybrid_score': rec['similarity'] * 0.6  # 60% weight for content-based
            }
        
        # Add CF-based with weight
        for rec in cf_based:
            if rec['content'].id in all_recommendations:
                all_recommendations[rec['content'].id]['cf_score'] = rec['cf_score']
                all_recommendations[rec['content'].id]['hybrid_score'] += rec['cf_score'] * 0.4  # 40% weight for CF
            else:
                all_recommendations[rec['content'].id] = {
                    'content': rec['content'],
                    'content_score': 0,
                    'cf_score': rec['cf_score'],
                    'hybrid_score': rec['cf_score'] * 0.4
                }
        
        # Sort by hybrid score
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )
        
        return sorted_recommendations[:limit]
        
    except Exception as e:
        logging.error(f"Error in hybrid recommendations: {e}")
        return get_content_recommendations(content_id, limit)

# Content categories
CONTENT_CATEGORIES = [
    'Blog Post',
    'News Article', 
    'Product Description',
    'About Page',
    'Landing Page',
    'Documentation',
    'Other'
]

# Content status options
CONTENT_STATUS = [
    'Draft',
    'Published',
    'Archived'
]

@app.route('/')
def index():
    """Homepage displaying different content based on authentication status"""
    # Show main content dashboard
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '').lower()
    
    # Build query with filters
    query = Content.query
    
    if category_filter:
        query = query.filter(Content.category == category_filter)
    if status_filter:
        query = query.filter(Content.status == status_filter)
    if search_query:
        query = query.filter(
            db.or_(
                Content.title.ilike(f'%{search_query}%'),
                Content.content.ilike(f'%{search_query}%')
            )
        )
    
    content_list = query.order_by(Content.updated_at.desc()).all()
    
    # Convert to dictionary format for template compatibility
    filtered_content = {content.id: content.to_dict() for content in content_list}
    
    # Get trending content for sidebar
    trending = get_trending_content(limit=5)
    
    return render_template('index.html', 
                         content_store=filtered_content,
                         categories=CONTENT_CATEGORIES,
                         statuses=CONTENT_STATUS,
                         current_category=category_filter,
                         current_status=status_filter,
                         current_search=request.args.get('search', ''),
                         trending=trending)

@app.route('/create', methods=['GET', 'POST'])
def create_content():
    """Create new content"""
    form = ContentForm()
    form.category.choices = [(cat, cat) for cat in CONTENT_CATEGORIES]
    form.status.choices = [(status, status) for status in CONTENT_STATUS]
    
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                image_filename = save_uploaded_file(file)
                if not image_filename:
                    flash('Invalid image file. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG files.', 'error')
                    return render_template('create_content.html', form=form)

        # Handle tags safely
        tags_data = form.tags.data or ''
        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()] if tags_data else []

        # Create new content in database
        new_content = Content(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            status=form.status.data,
            author=form.author.data,
            image=image_filename
        )
        new_content.set_tags_list(tags_list)
        
        try:
            db.session.add(new_content)
            db.session.commit()
            flash(f'Content "{new_content.title}" created successfully!', 'success')
            return redirect(url_for('view_content', content_id=new_content.id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating content. Please try again.', 'error')
            app.logger.error(f'Error creating content: {e}')
    
    return render_template('create_content.html', form=form)

@app.route('/content/<int:content_id>')
def view_content(content_id):
    """View single content item with recommendations"""
    content = Content.query.get_or_404(content_id)
    
    # Track user interaction
    track_user_interaction(content_id, 'view', score=1.0)
    
    # Get hybrid recommendations (combines content-based and collaborative filtering)
    recommendations = get_hybrid_recommendations(content_id, limit=4)
    category_suggestions = get_category_recommendations(content.category, exclude_id=content_id, limit=3)
    
    return render_template('view_content.html', 
                         content=content.to_dict(),
                         recommendations=recommendations,
                         category_suggestions=category_suggestions)

@app.route('/edit/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    """Edit existing content"""
    content = Content.query.get_or_404(content_id)
    
    form = EditContentForm()
    form.category.choices = [(cat, cat) for cat in CONTENT_CATEGORIES]
    form.status.choices = [(status, status) for status in CONTENT_STATUS]
    
    if form.validate_on_submit():
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                new_image = save_uploaded_file(file)
                if new_image:
                    # Remove old image if it exists
                    if content.image:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], content.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    content.image = new_image
                else:
                    flash('Invalid image file. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG files.', 'error')
                    return render_template('edit_content.html', form=form, content=content.to_dict())

        # Handle tags safely
        tags_data = form.tags.data or ''
        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()] if tags_data else []

        # Update content fields
        content.title = form.title.data
        content.content = form.content.data
        content.category = form.category.data
        content.status = form.status.data
        content.author = form.author.data
        content.set_tags_list(tags_list)
        content.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash(f'Content "{content.title}" updated successfully!', 'success')
            return redirect(url_for('view_content', content_id=content_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating content. Please try again.', 'error')
            app.logger.error(f'Error updating content: {e}')
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.title.data = content.title
        form.content.data = content.content
        form.category.data = content.category
        form.status.data = content.status
        form.author.data = content.author
        form.tags.data = ', '.join(content.get_tags_list())
    
    return render_template('edit_content.html', form=form, content=content.to_dict())

@app.route('/delete/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    """Delete content"""
    content = Content.query.get_or_404(content_id)
    title = content.title
    
    # Remove associated image file if it exists
    if content.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], content.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    try:
        db.session.delete(content)
        db.session.commit()
        flash(f'Content "{title}" deleted successfully!', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting content. Please try again.', 'error')
        app.logger.error(f'Error deleting content: {e}')
    
    return redirect(url_for('index'))

@app.route('/api/content/<int:content_id>/status', methods=['POST'])
def update_content_status(content_id):
    """Update content status via AJAX"""
    content = Content.query.get_or_404(content_id)
    
    json_data = request.get_json()
    new_status = json_data.get('status') if json_data else None
    if new_status not in CONTENT_STATUS:
        abort(400)
    
    content.status = new_status
    content.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return {'success': True, 'status': new_status}
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating content status: {e}')
        abort(500)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/gallery')
def image_gallery():
    """Display all images in a gallery view"""
    content_with_images = Content.query.filter(Content.image.isnot(None)).order_by(Content.created_at.desc()).all()
    
    images = []
    for content in content_with_images:
        images.append({
            'filename': content.image,
            'title': content.title,
            'content_id': content.id,
            'created_at': content.created_at,
            'author': content.author
        })
    
    return render_template('gallery.html', images=images)

@app.route('/trending')
def trending_content():
    """Display trending content"""
    trending = get_trending_content(limit=10)
    return render_template('trending.html', trending=trending)

@app.route('/analytics/cf')
def cf_analytics():
    """Collaborative Filtering Analytics Dashboard"""
    try:
        user_id = get_user_id()
        
        # Get user interaction statistics
        total_interactions = UserInteraction.query.count()
        unique_users = UserInteraction.query.with_entities(UserInteraction.user_id).distinct().count()
        user_interactions = UserInteraction.query.filter_by(user_id=user_id).count()
        
        # Get recent interactions
        recent_interactions = UserInteraction.query.order_by(
            UserInteraction.timestamp.desc()
        ).limit(10).all()
        
        # Get most popular content
        popular_content = db.session.query(
            Content.id, Content.title, func.count(UserInteraction.id).label('interaction_count')
        ).join(UserInteraction).group_by(Content.id, Content.title).order_by(
            func.count(UserInteraction.id).desc()
        ).limit(5).all()
        
        # Get user similarity data (if enough data exists)
        similar_users = []
        try:
            user_item_matrix, users, items = build_user_item_matrix()
            if user_id in user_item_matrix and len(users) > 1:
                target_user_items = user_item_matrix[user_id]
                for other_user in users[:5]:  # Check top 5 users
                    if other_user != user_id:
                        similarity = calculate_user_similarity(target_user_items, user_item_matrix[other_user])
                        if similarity > 0:
                            similar_users.append({
                                'user_id': other_user[:8] + '...',  # Truncate for privacy
                                'similarity': round(similarity, 3)
                            })
        except Exception as e:
            logging.error(f"Error calculating user similarities: {e}")
        
        return render_template('cf_analytics.html',
                             total_interactions=total_interactions,
                             unique_users=unique_users,
                             user_interactions=user_interactions,
                             recent_interactions=recent_interactions,
                             popular_content=popular_content,
                             similar_users=similar_users)
    except Exception as e:
        logging.error(f"Error in CF analytics: {e}")
        return render_template('cf_analytics.html', error=str(e))

@app.route('/demo/collaborative-filtering')
def cf_demo():
    """Collaborative Filtering demonstration page"""
    return render_template('cf_demo.html')

@app.route('/demo/cf-visual')
def cf_visual():
    """Visual collaborative filtering demonstration"""
    return render_template('cf_visual.html')

@app.route('/recommendations/<int:content_id>')
def content_recommendations(content_id):
    """API endpoint for getting content recommendations"""
    recommendations = get_hybrid_recommendations(content_id, limit=6)
    return {
        'recommendations': [
            {
                'id': rec['content'].id,
                'title': rec['content'].title,
                'category': rec['content'].category,
                'author': rec['content'].author,
                'hybrid_score': round(rec.get('hybrid_score', 0), 2),
                'cf_score': round(rec.get('cf_score', 0), 2),
                'content_score': round(rec.get('content_score', 0), 2),
                'url': url_for('view_content', content_id=rec['content'].id)
            }
            for rec in recommendations
        ]
    }

@app.route('/admin/database')
def database_admin():
    """Database administration dashboard"""
    try:
        # Get health status
        connection_ok, connection_msg = DatabaseHealthChecker.check_connection()
        integrity_ok, integrity_issues = DatabaseHealthChecker.check_table_integrity()
        
        health_status = {
            'connection': connection_ok,
            'integrity': integrity_ok,
            'connection_msg': connection_msg,
            'integrity_issues': integrity_issues
        }
        
        # Get database statistics
        stats = DatabaseManager.get_database_statistics()
        
        # Calculate totals
        stats['total_content'] = Content.query.count()
        stats['total_interactions'] = UserInteraction.query.count()
        
        return render_template('database_admin.html', 
                             health_status=health_status,
                             stats=stats)
    except Exception as e:
        logging.error(f"Error in database admin: {e}")
        return render_template('database_admin.html', 
                             health_status={'connection': False, 'integrity': False},
                             stats={}, error=str(e))

@app.route('/admin/db/optimize', methods=['POST'])
def optimize_database():
    """Optimize database performance"""
    try:
        success = DatabaseManager.optimize_database()
        return {'success': success}
    except Exception as e:
        logging.error(f"Database optimization error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/backup', methods=['POST'])
def create_database_backup():
    """Create database backup"""
    try:
        success, result = DatabaseManager.create_database_backup()
        return {'success': success, 'filename': result if success else None, 'error': result if not success else None}
    except Exception as e:
        logging.error(f"Database backup error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/update-search', methods=['POST'])
def update_search_vectors():
    """Update full-text search vectors"""
    try:
        DatabaseManager.create_full_text_search_triggers()
        success = DatabaseManager.update_all_search_vectors()
        return {'success': success}
    except Exception as e:
        logging.error(f"Search vector update error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/create-indexes', methods=['POST'])
def create_database_indexes():
    """Create additional database indexes"""
    try:
        success = DatabaseManager.create_database_indexes()
        return {'success': success}
    except Exception as e:
        logging.error(f"Index creation error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/cleanup', methods=['POST'])
def cleanup_old_data():
    """Clean up old user interactions"""
    try:
        deleted = DatabaseManager.cleanup_old_interactions()
        return {'success': True, 'deleted': deleted}
    except Exception as e:
        logging.error(f"Data cleanup error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/health')
def database_health():
    """Get database health status"""
    try:
        connection_ok, connection_msg = DatabaseHealthChecker.check_connection()
        integrity_ok, integrity_issues = DatabaseHealthChecker.check_table_integrity()
        
        return {
            'connection': connection_ok,
            'integrity': integrity_ok,
            'connection_msg': connection_msg,
            'issues': integrity_issues if not integrity_ok else []
        }
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {'connection': False, 'integrity': False, 'error': str(e)}

@app.route('/admin/db/search')
def full_text_search():
    """Full-text search endpoint"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return {'results': []}
        
        results = DatabaseManager.full_text_search(query)
        formatted_results = []
        
        for row in results:
            formatted_results.append({
                'id': row.id,
                'title': row.title,
                'content': row.content,
                'category': row.category,
                'author': row.author,
                'rank': float(row.rank)
            })
        
        return {'results': formatted_results}
    except Exception as e:
        logging.error(f"Full-text search error: {e}")
        return {'results': [], 'error': str(e)}

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('base.html', 
                         error_message="Content not found",
                         error_description="The content you're looking for doesn't exist."), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
