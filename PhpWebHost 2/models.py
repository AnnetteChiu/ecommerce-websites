from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, CheckConstraint, text
from sqlalchemy.dialects.postgresql import TSVECTOR

db = SQLAlchemy()

class Content(db.Model):
    """Content model for storing dynamic content with images"""
    __tablename__ = 'content'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    tags = db.Column(db.Text)  # Store tags as comma-separated string
    image = db.Column(db.String(255))  # Store image filename
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    search_vector = db.Column(TSVECTOR)  # Full-text search vector
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("LENGTH(title) >= 1", name='content_title_length_check'),
        CheckConstraint("LENGTH(content) >= 1", name='content_body_length_check'),
        CheckConstraint("status IN ('Draft', 'Published', 'Archived')", name='content_status_check'),
        Index('idx_content_search', 'search_vector', postgresql_using='gin'),
        Index('idx_content_created_status', 'created_at', 'status'),
        Index('idx_content_category_status', 'category', 'status'),
    )
    
    def __init__(self, title, content, category, status, author, image=None):
        self.title = title
        self.content = content
        self.category = category
        self.status = status
        self.author = author
        self.image = image
    
    def __repr__(self):
        return f'<Content {self.title}>'
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Set tags from a list"""
        if tags_list:
            self.tags = ', '.join(tags_list)
        else:
            self.tags = ''
    
    def to_dict(self):
        """Convert content to dictionary for compatibility with existing templates"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'status': self.status,
            'author': self.author,
            'tags': self.get_tags_list(),
            'image': self.image,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class UserInteraction(db.Model):
    """Track user interactions for collaborative filtering"""
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False, index=True)
    interaction_type = db.Column(db.String(50), nullable=False, index=True)
    interaction_score = db.Column(db.Float, default=1.0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship
    content = db.relationship('Content', backref=db.backref('interactions', lazy=True, cascade='all, delete-orphan'))
    
    # Database constraints and indexes
    __table_args__ = (
        CheckConstraint("interaction_score >= 0", name='interaction_score_positive_check'),
        CheckConstraint("interaction_type IN ('view', 'edit', 'like', 'share', 'delete')", name='interaction_type_check'),
        Index('idx_user_content', 'user_id', 'content_id'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_content_type_timestamp', 'content_id', 'interaction_type', 'timestamp'),
    )
    
    def __init__(self, user_id, content_id, interaction_type, interaction_score=1.0):
        self.user_id = user_id
        self.content_id = content_id
        self.interaction_type = interaction_type
        self.interaction_score = interaction_score
    
    def __repr__(self):
        return f'<UserInteraction {self.user_id} -> {self.content_id} ({self.interaction_type})>'




