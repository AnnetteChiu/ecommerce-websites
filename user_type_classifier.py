"""
User Type Classification System
Automatically classifies content for tech users, business users, or mixed audiences
"""

import re
from typing import Dict, List


class UserTypeClassifier:
    """Intelligent content classification system for user types"""
    
    def __init__(self):
        # Technical keywords and patterns
        self.tech_keywords = {
            'programming': ['code', 'programming', 'development', 'software', 'api', 'database', 
                          'algorithm', 'framework', 'library', 'python', 'javascript', 'react',
                          'node.js', 'sql', 'html', 'css', 'git', 'github', 'docker', 'kubernetes',
                          'cloud', 'aws', 'azure', 'deployment', 'server', 'backend', 'frontend',
                          'full-stack', 'devops', 'ci/cd', 'testing', 'debugging', 'refactoring'],
            'tech_concepts': ['machine learning', 'ai', 'artificial intelligence', 'data science',
                            'cybersecurity', 'blockchain', 'iot', 'automation', 'integration',
                            'architecture', 'microservices', 'scalability', 'performance',
                            'optimization', 'analytics', 'big data', 'neural network'],
            'technical_roles': ['developer', 'engineer', 'programmer', 'architect', 'devops',
                              'data scientist', 'analyst', 'technical lead', 'cto', 'tech team']
        }
        
        # Business keywords and patterns
        self.business_keywords = {
            'strategy': ['strategy', 'business model', 'revenue', 'profit', 'growth', 'market',
                        'customer', 'client', 'sales', 'marketing', 'roi', 'kpi', 'metrics',
                        'budget', 'finance', 'investment', 'stakeholder', 'partnership'],
            'management': ['management', 'leadership', 'team', 'project management', 'agile',
                          'scrum', 'planning', 'roadmap', 'milestone', 'delivery', 'timeline',
                          'resource', 'allocation', 'efficiency', 'productivity', 'workflow'],
            'business_roles': ['manager', 'director', 'ceo', 'cfo', 'cmo', 'vp', 'executive',
                             'business analyst', 'product manager', 'project manager', 'consultant',
                             'stakeholder', 'decision maker']
        }
        
        # Categories that typically indicate user type
        self.category_mapping = {
            'tech': ['Tutorial', 'Documentation', 'Technical Guide', 'API Reference'],
            'business': ['Business Plan', 'Market Analysis', 'Strategy Document', 'Financial Report'],
            'mixed': ['Product Description', 'Blog Post', 'News Article', 'General Content']
        }
    
    def classify_content(self, title: str, content: str, category: str, tags: List[str] = None) -> str:
        """
        Classify content into tech, business, or mixed user types
        
        Args:
            title: Content title
            content: Content body
            category: Content category
            tags: List of tags
            
        Returns:
            str: 'tech', 'business', or 'mixed'
        """
        # Combine all text for analysis
        full_text = f"{title} {content} {' '.join(tags or [])}"
        full_text = full_text.lower()
        
        # Calculate scores for each user type
        tech_score = self._calculate_tech_score(full_text, category)
        business_score = self._calculate_business_score(full_text, category)
        
        # Determine classification based on scores
        if tech_score > business_score and tech_score > 0.3:
            return 'tech'
        elif business_score > tech_score and business_score > 0.3:
            return 'business'
        else:
            return 'mixed'
    
    def _calculate_tech_score(self, text: str, category: str) -> float:
        """Calculate technical relevance score"""
        score = 0.0
        word_count = len(text.split())
        
        if word_count == 0:
            return 0.0
        
        # Category-based scoring
        if category in self.category_mapping.get('tech', []):
            score += 0.4
        
        # Keyword-based scoring
        for keyword_type, keywords in self.tech_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if keyword_type == 'programming':
                score += matches * 0.08  # Higher weight for programming terms
            elif keyword_type == 'tech_concepts':
                score += matches * 0.06
            else:
                score += matches * 0.04
        
        # Technical pattern recognition
        if re.search(r'\b(function|class|import|export|const|let|var)\b', text):
            score += 0.2
        if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', text, re.IGNORECASE):
            score += 0.15
        if re.search(r'[a-zA-Z]+\.[a-zA-Z]+\([^)]*\)', text):  # Method calls
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_business_score(self, text: str, category: str) -> float:
        """Calculate business relevance score"""
        score = 0.0
        word_count = len(text.split())
        
        if word_count == 0:
            return 0.0
        
        # Category-based scoring
        if category in self.category_mapping.get('business', []):
            score += 0.4
        
        # Keyword-based scoring
        for keyword_type, keywords in self.business_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if keyword_type == 'strategy':
                score += matches * 0.08  # Higher weight for strategy terms
            elif keyword_type == 'management':
                score += matches * 0.06
            else:
                score += matches * 0.04
        
        # Business pattern recognition
        if re.search(r'\$[\d,]+|\b\d+%|\bQ[1-4]\b|\bFY\d{4}\b', text):  # Financial patterns
            score += 0.15
        if re.search(r'\b(increase|decrease|growth|decline) (by|of) \d+%', text):
            score += 0.1
        if re.search(r'\b(revenue|profit|loss|budget|cost)\b', text):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_classification_explanation(self, title: str, content: str, category: str, tags: List[str] = None) -> Dict:
        """
        Get detailed explanation of classification
        
        Returns:
            Dict with classification details and reasoning
        """
        full_text = f"{title} {content} {' '.join(tags or [])}".lower()
        tech_score = self._calculate_tech_score(full_text, category)
        business_score = self._calculate_business_score(full_text, category)
        classification = self.classify_content(title, content, category, tags)
        
        # Find matching keywords
        tech_matches = []
        business_matches = []
        
        for keyword_group in self.tech_keywords.values():
            tech_matches.extend([kw for kw in keyword_group if kw in full_text])
        
        for keyword_group in self.business_keywords.values():
            business_matches.extend([kw for kw in keyword_group if kw in full_text])
        
        return {
            'classification': classification,
            'tech_score': round(tech_score, 3),
            'business_score': round(business_score, 3),
            'tech_keywords': tech_matches[:10],  # Limit to top 10
            'business_keywords': business_matches[:10],
            'reasoning': self._get_reasoning(classification, tech_score, business_score, category)
        }
    
    def _get_reasoning(self, classification: str, tech_score: float, business_score: float, category: str) -> str:
        """Generate human-readable reasoning for classification"""
        if classification == 'tech':
            return f"Classified as Tech content due to high technical score ({tech_score:.2f}) with technical keywords and patterns."
        elif classification == 'business':
            return f"Classified as Business content due to high business score ({business_score:.2f}) with business-focused language."
        else:
            return f"Classified as Mixed content with balanced scores (Tech: {tech_score:.2f}, Business: {business_score:.2f}) or general content."


def classify_existing_content():
    """Classify all existing content in the database"""
    from app import db
    from models import Content
    
    classifier = UserTypeClassifier()
    contents = Content.query.all()
    
    updated_count = 0
    for content in contents:
        if not content.user_type or content.user_type == 'mixed':
            tags_list = content.get_tags_list() if hasattr(content, 'get_tags_list') else []
            user_type = classifier.classify_content(
                content.title,
                content.content,
                content.category,
                tags_list
            )
            
            content.user_type = user_type
            updated_count += 1
    
    db.session.commit()
    return updated_count


def batch_classify_content(content_ids: List[int]) -> Dict[int, str]:
    """
    Classify multiple content items by ID
    
    Args:
        content_ids: List of content IDs to classify
        
    Returns:
        Dict mapping content ID to user type
    """
    from app import db
    from models import Content
    
    classifier = UserTypeClassifier()
    results = {}
    
    contents = Content.query.filter(Content.id.in_(content_ids)).all()
    
    for content in contents:
        tags_list = content.get_tags_list() if hasattr(content, 'get_tags_list') else []
        user_type = classifier.classify_content(
            content.title,
            content.content,
            content.category,
            tags_list
        )
        
        content.user_type = user_type
        results[content.id] = user_type
    
    db.session.commit()
    return results