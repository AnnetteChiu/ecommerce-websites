"""
Personalized Content Recommendation Engine
Provides intelligent content suggestions based on user behavior, preferences, and content analysis
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re
from models import db, Content, UserInteraction, User
from sqlalchemy import func, desc
import logging

class PersonalizedRecommendationEngine:
    """Advanced recommendation engine with multiple algorithms"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.content_features = None
        self.content_matrix = None
        self.svd_model = TruncatedSVD(n_components=50, random_state=42)
        self.user_profiles = {}
        
    def build_content_features(self):
        """Build TF-IDF features for all content"""
        try:
            contents = Content.query.filter_by(status='Published').all()
            if not contents:
                return
                
            # Combine text features for each content
            content_texts = []
            content_ids = []
            
            for content in contents:
                # Combine title, content, tags, category, and author
                combined_text = f"{content.title} {content.content} {content.tags or ''} {content.category} {content.author}"
                # Clean HTML and normalize text
                clean_text = re.sub(r'<[^>]+>', '', combined_text.lower())
                content_texts.append(clean_text)
                content_ids.append(content.id)
            
            # Build TF-IDF matrix
            self.content_matrix = self.tfidf_vectorizer.fit_transform(content_texts)
            self.content_features = dict(zip(content_ids, range(len(content_ids))))
            
            logging.info(f"Built content features for {len(contents)} items")
            
        except Exception as e:
            logging.error(f"Error building content features: {e}")
    
    def analyze_user_behavior(self, user_id):
        """Analyze user's interaction patterns and preferences"""
        try:
            # Get user interactions in the last 90 days
            recent_date = datetime.utcnow() - timedelta(days=90)
            interactions = UserInteraction.query.filter(
                UserInteraction.user_id == user_id,
                UserInteraction.timestamp >= recent_date
            ).all()
            
            if not interactions:
                return self._get_default_preferences()
            
            # Analyze interaction patterns
            interaction_weights = {
                'view': 1.0,
                'edit': 3.0,
                'like': 2.0,
                'share': 2.5,
                'create': 4.0
            }
            
            category_scores = defaultdict(float)
            author_scores = defaultdict(float)
            tag_scores = defaultdict(float)
            time_decay_factor = 0.95  # Recent interactions weighted more
            
            for i, interaction in enumerate(sorted(interactions, key=lambda x: x.timestamp)):
                content = interaction.content
                if not content or content.status != 'Published':
                    continue
                
                # Time decay: more recent interactions have higher weight
                time_weight = time_decay_factor ** (len(interactions) - i - 1)
                interaction_weight = interaction_weights.get(interaction.interaction_type, 1.0)
                total_weight = interaction_weight * time_weight * interaction.interaction_score
                
                # Update category preferences
                category_scores[content.category] += total_weight
                
                # Update author preferences
                author_scores[content.author] += total_weight
                
                # Update tag preferences
                if content.tags:
                    tags = [tag.strip().lower() for tag in content.tags.split(',')]
                    for tag in tags:
                        tag_scores[tag] += total_weight * 0.5  # Tags weighted less than categories
            
            # Normalize scores
            max_category_score = max(category_scores.values()) if category_scores else 1
            max_author_score = max(author_scores.values()) if author_scores else 1
            max_tag_score = max(tag_scores.values()) if tag_scores else 1
            
            normalized_categories = {k: v/max_category_score for k, v in category_scores.items()}
            normalized_authors = {k: v/max_author_score for k, v in author_scores.items()}
            normalized_tags = {k: v/max_tag_score for k, v in tag_scores.items()}
            
            return {
                'categories': normalized_categories,
                'authors': normalized_authors,
                'tags': normalized_tags,
                'total_interactions': len(interactions),
                'recent_activity': len([i for i in interactions if i.timestamp >= datetime.utcnow() - timedelta(days=7)])
            }
            
        except Exception as e:
            logging.error(f"Error analyzing user behavior for {user_id}: {e}")
            return self._get_default_preferences()
    
    def _get_default_preferences(self):
        """Return default preferences for new users"""
        return {
            'categories': {},
            'authors': {},
            'tags': {},
            'total_interactions': 0,
            'recent_activity': 0
        }
    
    def get_content_based_recommendations(self, user_id, num_recommendations=10):
        """Generate recommendations based on content similarity"""
        try:
            if self.content_matrix is None:
                self.build_content_features()
            
            if self.content_matrix is None:
                return []
            
            # Get user's interaction history
            user_interactions = UserInteraction.query.filter_by(user_id=user_id).all()
            if not user_interactions:
                return self._get_trending_recommendations(num_recommendations)
            
            # Build user profile based on interacted content
            interacted_content_ids = list(set([i.content_id for i in user_interactions]))
            user_vector = np.zeros(self.content_matrix.shape[1])
            
            for content_id in interacted_content_ids:
                if content_id in self.content_features:
                    content_idx = self.content_features[content_id]
                    # Weight by interaction frequency and type
                    content_interactions = [i for i in user_interactions if i.content_id == content_id]
                    weight = sum([i.interaction_score for i in content_interactions])
                    user_vector += self.content_matrix[content_idx].toarray().flatten() * weight
            
            # Normalize user vector
            if np.linalg.norm(user_vector) > 0:
                user_vector = user_vector / np.linalg.norm(user_vector)
            
            # Calculate similarities with all content
            similarities = cosine_similarity([user_vector], self.content_matrix).flatten()
            
            # Get content recommendations
            content_similarities = []
            for content_id, content_idx in self.content_features.items():
                if content_id not in interacted_content_ids:  # Don't recommend already seen content
                    content_similarities.append((content_id, similarities[content_idx]))
            
            # Sort by similarity and return top recommendations
            content_similarities.sort(key=lambda x: x[1], reverse=True)
            recommended_ids = [content_id for content_id, _ in content_similarities[:num_recommendations]]
            
            return Content.query.filter(Content.id.in_(recommended_ids)).all()
            
        except Exception as e:
            logging.error(f"Error generating content-based recommendations: {e}")
            return self._get_trending_recommendations(num_recommendations)
    
    def get_collaborative_filtering_recommendations(self, user_id, num_recommendations=10):
        """Generate recommendations using collaborative filtering"""
        try:
            # Build user-item interaction matrix
            users = db.session.query(UserInteraction.user_id).distinct().all()
            contents = db.session.query(UserInteraction.content_id).distinct().all()
            
            if len(users) < 2 or len(contents) < 2:
                return self._get_trending_recommendations(num_recommendations)
            
            user_ids = [u[0] for u in users]
            content_ids = [c[0] for c in contents]
            
            # Create user-content interaction matrix
            interaction_matrix = np.zeros((len(user_ids), len(content_ids)))
            
            user_id_to_idx = {user_id: idx for idx, user_id in enumerate(user_ids)}
            content_id_to_idx = {content_id: idx for idx, content_id in enumerate(content_ids)}
            
            interactions = UserInteraction.query.all()
            for interaction in interactions:
                if interaction.user_id in user_id_to_idx and interaction.content_id in content_id_to_idx:
                    user_idx = user_id_to_idx[interaction.user_id]
                    content_idx = content_id_to_idx[interaction.content_id]
                    interaction_matrix[user_idx, content_idx] += interaction.interaction_score
            
            # Find similar users
            if user_id not in user_id_to_idx:
                return self._get_trending_recommendations(num_recommendations)
            
            target_user_idx = user_id_to_idx[user_id]
            user_similarities = cosine_similarity([interaction_matrix[target_user_idx]], interaction_matrix).flatten()
            
            # Get top similar users (excluding self)
            similar_users = []
            for idx, similarity in enumerate(user_similarities):
                if idx != target_user_idx and similarity > 0.1:  # Minimum similarity threshold
                    similar_users.append((user_ids[idx], similarity))
            
            similar_users.sort(key=lambda x: x[1], reverse=True)
            top_similar_users = similar_users[:10]  # Top 10 similar users
            
            # Generate recommendations based on similar users' preferences
            content_scores = defaultdict(float)
            target_user_interactions = set([i.content_id for i in UserInteraction.query.filter_by(user_id=user_id).all()])
            
            for similar_user_id, similarity in top_similar_users:
                similar_user_interactions = UserInteraction.query.filter_by(user_id=similar_user_id).all()
                
                for interaction in similar_user_interactions:
                    if interaction.content_id not in target_user_interactions:  # Don't recommend seen content
                        content_scores[interaction.content_id] += similarity * interaction.interaction_score
            
            # Sort and get top recommendations
            sorted_recommendations = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
            recommended_ids = [content_id for content_id, _ in sorted_recommendations[:num_recommendations]]
            
            return Content.query.filter(
                Content.id.in_(recommended_ids),
                Content.status == 'Published'
            ).all()
            
        except Exception as e:
            logging.error(f"Error generating collaborative filtering recommendations: {e}")
            return self._get_trending_recommendations(num_recommendations)
    
    def get_hybrid_recommendations(self, user_id, num_recommendations=10):
        """Generate hybrid recommendations combining multiple approaches"""
        try:
            # Get user preferences
            user_preferences = self.analyze_user_behavior(user_id)
            
            # Content-based recommendations (40% weight)
            content_based = self.get_content_based_recommendations(user_id, num_recommendations * 2)
            
            # Collaborative filtering recommendations (30% weight)
            collaborative = self.get_collaborative_filtering_recommendations(user_id, num_recommendations * 2)
            
            # Preference-based recommendations (30% weight)
            preference_based = self.get_preference_based_recommendations(user_id, user_preferences, num_recommendations * 2)
            
            # Combine and score recommendations
            recommendation_scores = defaultdict(float)
            seen_content = set()
            
            # Add content-based with weight 0.4
            for i, content in enumerate(content_based):
                if content.id not in seen_content:
                    recommendation_scores[content.id] += 0.4 * (1.0 - i * 0.05)  # Decreasing weight
                    seen_content.add(content.id)
            
            # Add collaborative filtering with weight 0.3
            for i, content in enumerate(collaborative):
                if content.id not in seen_content:
                    recommendation_scores[content.id] += 0.3 * (1.0 - i * 0.05)
                    seen_content.add(content.id)
                elif content.id in recommendation_scores:
                    recommendation_scores[content.id] += 0.3 * (1.0 - i * 0.05)
            
            # Add preference-based with weight 0.3
            for i, content in enumerate(preference_based):
                if content.id not in seen_content:
                    recommendation_scores[content.id] += 0.3 * (1.0 - i * 0.05)
                    seen_content.add(content.id)
                elif content.id in recommendation_scores:
                    recommendation_scores[content.id] += 0.3 * (1.0 - i * 0.05)
            
            # Sort by final scores
            sorted_recommendations = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
            final_content_ids = [content_id for content_id, _ in sorted_recommendations[:num_recommendations]]
            
            return Content.query.filter(Content.id.in_(final_content_ids)).all()
            
        except Exception as e:
            logging.error(f"Error generating hybrid recommendations: {e}")
            return self._get_trending_recommendations(num_recommendations)
    
    def get_preference_based_recommendations(self, user_id, user_preferences, num_recommendations=10):
        """Generate recommendations based on user preferences"""
        try:
            # Get content excluding already interacted items
            user_interactions = UserInteraction.query.filter_by(user_id=user_id).all()
            interacted_content_ids = [i.content_id for i in user_interactions]
            
            query = Content.query.filter(
                Content.status == 'Published',
                ~Content.id.in_(interacted_content_ids) if interacted_content_ids else True
            )
            
            all_content = query.all()
            content_scores = []
            
            for content in all_content:
                score = 0.0
                
                # Category preference
                if content.category in user_preferences['categories']:
                    score += user_preferences['categories'][content.category] * 2.0
                
                # Author preference
                if content.author in user_preferences['authors']:
                    score += user_preferences['authors'][content.author] * 1.5
                
                # Tag preferences
                if content.tags:
                    content_tags = [tag.strip().lower() for tag in content.tags.split(',')]
                    for tag in content_tags:
                        if tag in user_preferences['tags']:
                            score += user_preferences['tags'][tag] * 1.0
                
                # Boost recent content slightly
                days_old = (datetime.utcnow() - content.created_at).days
                recency_boost = max(0, 1.0 - days_old / 30.0) * 0.2
                score += recency_boost
                
                content_scores.append((content, score))
            
            # Sort by score and return top recommendations
            content_scores.sort(key=lambda x: x[1], reverse=True)
            return [content for content, _ in content_scores[:num_recommendations]]
            
        except Exception as e:
            logging.error(f"Error generating preference-based recommendations: {e}")
            return []
    
    def _get_trending_recommendations(self, num_recommendations=10):
        """Fallback to trending content for new users"""
        try:
            # Get recent popular content
            recent_date = datetime.utcnow() - timedelta(days=30)
            
            trending_content = db.session.query(
                Content,
                func.count(UserInteraction.id).label('interaction_count')
            ).outerjoin(UserInteraction).filter(
                Content.status == 'Published',
                Content.created_at >= recent_date
            ).group_by(Content.id).order_by(
                desc('interaction_count'),
                desc(Content.created_at)
            ).limit(num_recommendations).all()
            
            return [content for content, _ in trending_content]
            
        except Exception as e:
            logging.error(f"Error getting trending recommendations: {e}")
            return Content.query.filter_by(status='Published').order_by(desc(Content.created_at)).limit(num_recommendations).all()
    
    def track_recommendation_feedback(self, user_id, content_id, action):
        """Track user feedback on recommendations for improvement"""
        try:
            # Map actions to interaction types and scores
            action_mapping = {
                'clicked': ('view', 1.0),
                'liked': ('like', 2.0),
                'shared': ('share', 2.5),
                'dismissed': ('view', -0.5),
                'saved': ('like', 3.0)
            }
            
            if action in action_mapping:
                interaction_type, score = action_mapping[action]
                
                # Create or update interaction
                existing_interaction = UserInteraction.query.filter_by(
                    user_id=user_id,
                    content_id=content_id,
                    interaction_type=interaction_type
                ).first()
                
                if existing_interaction:
                    existing_interaction.interaction_score += score
                    existing_interaction.timestamp = datetime.utcnow()
                else:
                    new_interaction = UserInteraction(
                        user_id=user_id,
                        content_id=content_id,
                        interaction_type=interaction_type,
                        interaction_score=score
                    )
                    db.session.add(new_interaction)
                
                db.session.commit()
                logging.info(f"Tracked recommendation feedback: {user_id} -> {content_id} ({action})")
                
        except Exception as e:
            logging.error(f"Error tracking recommendation feedback: {e}")
            db.session.rollback()

# Global recommendation engine instance
recommendation_engine = PersonalizedRecommendationEngine()