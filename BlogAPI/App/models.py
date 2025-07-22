"""
Data Models Layer
=================
This module contains all database models for the blog platform.
Models define the structure and relationships of our data.
"""

from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from .db import db

class User(db.Model):
    """User model for authentication and author management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with posts
    posts = db.relationship('Post', backref='author_user', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='comment_author', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='voter', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Post(db.Model):
    """Blog post model with voting and search capabilities"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)  # Indexed for search
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # New foreign key
    published_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    
    # Voting relationships
    votes = db.relationship('Vote', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    @property
    def upvotes(self):
        """Calculate total upvotes"""
        return Vote.query.filter_by(post_id=self.id, vote_type=True).count()
    
    @property
    def downvotes(self):
        """Calculate total downvotes"""
        return Vote.query.filter_by(post_id=self.id, vote_type=False).count()
    
    @property
    def vote_score(self):
        """Calculate net vote score (upvotes - downvotes)"""
        return self.upvotes - self.downvotes
    
    @property
    def comment_count(self):
        """Get total number of comments"""
        return len(self.comments)
    
    def to_dict(self, include_votes=True):
        """Convert post object to dictionary"""
        result = {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'author': self.author,
            'author_id': self.author_id,
            'published_at': self.published_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_published': self.is_published,
            'comment_count': self.comment_count
        }
        
        if include_votes:
            result.update({
                'upvotes': self.upvotes,
                'downvotes': self.downvotes,
                'vote_score': self.vote_score
            })
        
        return result

class Vote(db.Model):
    """Vote model for upvotes and downvotes on posts"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    vote_type = db.Column(db.Boolean, nullable=False)  # True for upvote, False for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per post
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_vote'),)
    
    def to_dict(self):
        """Convert vote object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'vote_type': 'upvote' if self.vote_type else 'downvote',
            'created_at': self.created_at.isoformat()
        }

class Comment(db.Model):
    """Comment model for post discussions"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """Convert comment object to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'author_username': self.comment_author.username if self.comment_author else None,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
