"""
Product Collaborative Filtering Recommendation Engine
Recommends products based on user purchase behavior and interaction patterns
"""

import logging
from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np
from sqlalchemy import text
from app import db
from models import Product, Order, OrderItem, CartItem, User
import math

class ProductRecommendationEngine:
    """Collaborative filtering recommendation system for products"""
    
    def __init__(self):
        self.user_product_matrix = {}
        self.product_similarity_cache = {}
        
    def build_user_product_matrix(self) -> Dict:
        """Build user-product interaction matrix from orders and cart data"""
        try:
            # Get purchase data from completed orders
            purchase_query = text("""
                SELECT u.id as user_id, oi.product_id, SUM(oi.quantity) as interaction_score
                FROM users u
                JOIN orders o ON u.id = o.user_id
                JOIN order_items oi ON o.id = oi.order_id
                WHERE o.status = 'completed'
                GROUP BY u.id, oi.product_id
            """)
            
            # Get cart data as weaker signals
            cart_query = text("""
                SELECT u.id as user_id, ci.product_id, SUM(ci.quantity) * 0.3 as interaction_score
                FROM users u
                JOIN cart_items ci ON u.id = ci.user_id
                GROUP BY u.id, ci.product_id
            """)
            
            user_matrix = defaultdict(lambda: defaultdict(float))
            
            # Process purchase data (stronger signal)
            purchase_results = db.session.execute(purchase_query).fetchall()
            for row in purchase_results:
                user_matrix[row.user_id][row.product_id] += float(row.interaction_score)
            
            # Process cart data (weaker signal)
            cart_results = db.session.execute(cart_query).fetchall()
            for row in cart_results:
                user_matrix[row.user_id][row.product_id] += float(row.interaction_score)
            
            self.user_product_matrix = dict(user_matrix)
            logging.info(f"Built user-product matrix for {len(self.user_product_matrix)} users")
            return self.user_product_matrix
            
        except Exception as e:
            logging.error(f"Error building user-product matrix: {e}")
            return {}
    
    def calculate_user_similarity(self, user1_products: Dict, user2_products: Dict) -> float:
        """Calculate cosine similarity between two users based on product interactions"""
        try:
            # Get common products
            common_products = set(user1_products.keys()) & set(user2_products.keys())
            
            if len(common_products) == 0:
                return 0.0
            
            # Calculate vectors for common products only
            user1_vector = [user1_products[product] for product in common_products]
            user2_vector = [user2_products[product] for product in common_products]
            
            # Calculate cosine similarity
            dot_product = sum(u1 * u2 for u1, u2 in zip(user1_vector, user2_vector))
            magnitude1 = math.sqrt(sum(u1 ** 2 for u1 in user1_vector))
            magnitude2 = math.sqrt(u2 ** 2 for u2 in user2_vector)
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, similarity)  # Ensure non-negative similarity
            
        except Exception as e:
            logging.error(f"Error calculating user similarity: {e}")
            return 0.0
    
    def get_user_based_recommendations(self, target_user_id: str, limit: int = 5) -> List[Dict]:
        """Get product recommendations using user-based collaborative filtering"""
        try:
            if not self.user_product_matrix:
                self.build_user_product_matrix()
            
            if target_user_id not in self.user_product_matrix:
                return self.get_popular_products(limit)
            
            target_user_products = self.user_product_matrix[target_user_id]
            user_similarities = []
            
            # Calculate similarities with other users
            for user_id, user_products in self.user_product_matrix.items():
                if user_id != target_user_id:
                    similarity = self.calculate_user_similarity(target_user_products, user_products)
                    if similarity > 0.1:  # Only consider users with meaningful similarity
                        user_similarities.append((user_id, similarity))
            
            # Sort by similarity and get top similar users
            user_similarities.sort(key=lambda x: x[1], reverse=True)
            top_similar_users = user_similarities[:10]  # Top 10 similar users
            
            if not top_similar_users:
                return self.get_popular_products(limit)
            
            # Aggregate product scores from similar users
            product_scores = defaultdict(float)
            total_similarity = sum(sim for _, sim in top_similar_users)
            
            for similar_user_id, similarity in top_similar_users:
                similar_user_products = self.user_product_matrix[similar_user_id]
                weight = similarity / total_similarity
                
                for product_id, score in similar_user_products.items():
                    # Don't recommend products the user already has
                    if product_id not in target_user_products:
                        product_scores[product_id] += score * weight
            
            # Sort recommendations by score
            sorted_recommendations = sorted(product_scores.items(), 
                                          key=lambda x: x[1], reverse=True)
            
            # Get product details
            recommended_products = []
            for product_id, score in sorted_recommendations[:limit]:
                product = Product.query.get(product_id)
                if product and product.is_active:
                    recommended_products.append({
                        'product': product,
                        'score': score,
                        'reason': 'Users with similar preferences also liked this product'
                    })
            
            return recommended_products
            
        except Exception as e:
            logging.error(f"Error getting user-based recommendations: {e}")
            return self.get_popular_products(limit)
    
    def get_item_based_recommendations(self, product_id: int, limit: int = 5) -> List[Dict]:
        """Get product recommendations using item-based collaborative filtering"""
        try:
            if not self.user_product_matrix:
                self.build_user_product_matrix()
            
            # Build product similarity matrix
            product_users = defaultdict(dict)
            for user_id, products in self.user_product_matrix.items():
                for pid, score in products.items():
                    product_users[pid][user_id] = score
            
            if product_id not in product_users:
                return self.get_popular_products(limit)
            
            target_product_users = product_users[product_id]
            product_similarities = []
            
            # Calculate similarities with other products
            for pid, pid_users in product_users.items():
                if pid != product_id:
                    similarity = self.calculate_user_similarity(target_product_users, pid_users)
                    if similarity > 0.1:
                        product_similarities.append((pid, similarity))
            
            # Sort by similarity
            product_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get product details
            recommended_products = []
            for pid, similarity in product_similarities[:limit]:
                product = Product.query.get(pid)
                if product and product.is_active:
                    recommended_products.append({
                        'product': product,
                        'score': similarity,
                        'reason': 'Customers who bought this item also bought'
                    })
            
            return recommended_products
            
        except Exception as e:
            logging.error(f"Error getting item-based recommendations: {e}")
            return self.get_popular_products(limit)
    
    def get_category_based_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recommendations based on user's preferred categories"""
        try:
            # Get user's category preferences from purchase history
            category_query = text("""
                SELECT p.category, SUM(oi.quantity) as total_purchased
                FROM users u
                JOIN orders o ON u.id = o.user_id
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE u.id = :user_id AND o.status = 'completed'
                GROUP BY p.category
                ORDER BY total_purchased DESC
                LIMIT 3
            """)
            
            results = db.session.execute(category_query, {'user_id': user_id}).fetchall()
            
            if not results:
                return self.get_popular_products(limit)
            
            preferred_categories = [row.category for row in results]
            
            # Get top products from preferred categories that user hasn't bought
            purchased_query = text("""
                SELECT DISTINCT oi.product_id
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = :user_id AND o.status = 'completed'
            """)
            
            purchased_results = db.session.execute(purchased_query, {'user_id': user_id}).fetchall()
            purchased_product_ids = [row.product_id for row in purchased_results]
            
            # Get recommendations from preferred categories
            recommended_products = []
            for category in preferred_categories:
                products = Product.query.filter(
                    Product.category == category,
                    Product.is_active == True,
                    ~Product.id.in_(purchased_product_ids) if purchased_product_ids else True
                ).order_by(Product.created_at.desc()).limit(limit).all()
                
                for product in products:
                    if len(recommended_products) < limit:
                        recommended_products.append({
                            'product': product,
                            'score': 0.8,  # High score for category preference
                            'reason': f'Based on your interest in {category}'
                        })
            
            return recommended_products[:limit]
            
        except Exception as e:
            logging.error(f"Error getting category-based recommendations: {e}")
            return self.get_popular_products(limit)
    
    def get_hybrid_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get hybrid recommendations combining multiple approaches"""
        try:
            recommendations = []
            
            # Get recommendations from different methods
            user_based = self.get_user_based_recommendations(user_id, limit//2 + 1)
            category_based = self.get_category_based_recommendations(user_id, limit//2 + 1)
            
            # Combine and deduplicate
            seen_products = set()
            
            # Add user-based recommendations (higher weight)
            for rec in user_based:
                if rec['product'].id not in seen_products:
                    rec['score'] *= 1.2  # Boost user-based recommendations
                    recommendations.append(rec)
                    seen_products.add(rec['product'].id)
            
            # Add category-based recommendations
            for rec in category_based:
                if rec['product'].id not in seen_products and len(recommendations) < limit:
                    recommendations.append(rec)
                    seen_products.add(rec['product'].id)
            
            # Fill remaining slots with popular products
            if len(recommendations) < limit:
                popular = self.get_popular_products(limit - len(recommendations))
                for rec in popular:
                    if rec['product'].id not in seen_products:
                        recommendations.append(rec)
                        seen_products.add(rec['product'].id)
            
            return recommendations[:limit]
            
        except Exception as e:
            logging.error(f"Error getting hybrid recommendations: {e}")
            return self.get_popular_products(limit)
    
    def get_popular_products(self, limit: int = 5) -> List[Dict]:
        """Get popular products as fallback recommendations"""
        try:
            # Get products with most sales
            popular_query = text("""
                SELECT p.id, p.name, COALESCE(SUM(oi.quantity), 0) as total_sold
                FROM products p
                LEFT JOIN order_items oi ON p.id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
                WHERE p.is_active = true
                GROUP BY p.id, p.name
                ORDER BY total_sold DESC, p.created_at DESC
                LIMIT :limit
            """)
            
            results = db.session.execute(popular_query, {'limit': limit}).fetchall()
            
            popular_products = []
            for row in results:
                product = Product.query.get(row.id)
                if product:
                    popular_products.append({
                        'product': product,
                        'score': 0.5,
                        'reason': 'Popular product'
                    })
            
            return popular_products
            
        except Exception as e:
            logging.error(f"Error getting popular products: {e}")
            return []

# Global instance
product_recommendation_engine = ProductRecommendationEngine()

def get_product_recommendations_for_user(user_id: str, recommendation_type: str = 'hybrid', limit: int = 5) -> List[Dict]:
    """
    Get product recommendations for a user
    
    Args:
        user_id: User ID
        recommendation_type: 'user_based', 'category_based', 'hybrid'
        limit: Number of recommendations
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        if recommendation_type == 'user_based':
            return product_recommendation_engine.get_user_based_recommendations(user_id, limit)
        elif recommendation_type == 'category_based':
            return product_recommendation_engine.get_category_based_recommendations(user_id, limit)
        elif recommendation_type == 'hybrid':
            return product_recommendation_engine.get_hybrid_recommendations(user_id, limit)
        else:
            return product_recommendation_engine.get_popular_products(limit)
            
    except Exception as e:
        logging.error(f"Error getting product recommendations: {e}")
        return product_recommendation_engine.get_popular_products(limit)

def get_user_recommendations(user_id, limit=6):
    """Get personalized recommendations for a specific user - simplified interface"""
    try:
        recommendations = product_recommendation_engine.get_hybrid_recommendations(user_id, limit)
        # Extract just the products from the recommendation objects
        return [rec['product'] for rec in recommendations if 'product' in rec]
    except Exception as e:
        logging.error(f"Error getting user recommendations: {e}")
        return get_popular_products(limit)

def get_popular_products(limit=6):
    """Get popular products based on order frequency - simplified interface"""
    try:
        recommendations = product_recommendation_engine.get_popular_products(limit)
        # Extract just the products from the recommendation objects
        return [rec['product'] for rec in recommendations if 'product' in rec]
    except Exception as e:
        logging.error(f"Error getting popular products: {e}")
        # Ultimate fallback to newest products
        from app import Product
        return Product.query.filter_by(is_active=True)\
                          .order_by(Product.created_at.desc())\
                          .limit(limit).all()

def get_similar_products(product_id: int, limit: int = 5) -> List[Dict]:
    """
    Get products similar to a given product
    
    Args:
        product_id: ID of the product to find similar items for
        limit: Number of similar products to return
        
    Returns:
        List of similar product dictionaries
    """
    try:
        return product_recommendation_engine.get_item_based_recommendations(product_id, limit)
    except Exception as e:
        logging.error(f"Error getting similar products: {e}")
        return product_recommendation_engine.get_popular_products(limit)