"""
Service Layer
=============
This module contains business logic and operations for the blog platform.
Services handle complex operations and business rules.
"""

from datetime import datetime
from flask import current_app
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from .models import Post, User, Vote, Comment
from .db import db

class PostService:
    """Service class for post-related business operations"""
    
    @staticmethod
    def create_post(title, body, author, author_id=None):
        """Create a new blog post"""
        try:
            post = Post(
                title=title.strip(),
                body=body.strip(),
                author=author.strip(),
                author_id=author_id
            )
            db.session.add(post)
            db.session.commit()
            current_app.logger.info(f"Post created with ID: {post.id}")
            return post, None
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error creating post: {str(e)}")
            return None, "Error creating post due to constraint violation"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_post_by_id(post_id):
        """Get a single post by ID"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"
            return post, None
        except Exception as e:
            current_app.logger.error(f"Error fetching post {post_id}: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_all_posts(page=1, per_page=10, sort_by='published_at', order='desc'):
        """Get paginated list of posts with sorting"""
        try:
            # Determine sort column
            sort_column = getattr(Post, sort_by, Post.published_at)
            
            # Apply ordering
            if order.lower() == 'desc':
                sort_column = sort_column.desc()
            
            posts = Post.query.filter_by(is_published=True)\
                             .order_by(sort_column)\
                             .paginate(
                                 page=page, 
                                 per_page=per_page, 
                                 error_out=False
                             )
            
            return posts, None
        except Exception as e:
            current_app.logger.error(f"Error fetching posts: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def search_posts(query, page=1, per_page=10):
        """Search posts by title and content"""
        try:
            if not query or not query.strip():
                return PostService.get_all_posts(page, per_page)
            
            search_term = f"%{query.strip()}%"
            posts = Post.query.filter(
                db.and_(
                    Post.is_published == True,
                    db.or_(
                        Post.title.ilike(search_term),
                        Post.body.ilike(search_term)
                    )
                )
            ).order_by(Post.published_at.desc())\
             .paginate(page=page, per_page=per_page, error_out=False)
            
            return posts, None
        except Exception as e:
            current_app.logger.error(f"Error searching posts: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def update_post(post_id, title=None, body=None, author_id=None):
        """Update an existing post"""
        try:
            # Use a transaction to prevent concurrent modifications
            with db.session.begin_nested():
                post = Post.query.get(post_id)
                if not post:
                    return None, "Post not found"
                
                if title:
                    post.title = title.strip()
                if body:
                    post.body = body.strip()
                if author_id:
                    post.author_id = author_id
                
                post.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            current_app.logger.info(f"Post {post_id} updated")
            return post, None
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error updating post {post_id}: {str(e)}")
            return None, "Error updating post due to constraint violation"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating post {post_id}: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def delete_post(post_id, author_id=None):
        """Delete a post (only by author or admin)"""
        try:
            # Use a transaction to prevent concurrent modifications
            with db.session.begin_nested():
                post = Post.query.get(post_id)
                if not post:
                    return False, "Post not found"
                
                # Check authorization (if author_id provided)
                if author_id and post.author_id != author_id:
                    return False, "Unauthorized to delete this post"
                
                db.session.delete(post)
            
            db.session.commit()
            
            current_app.logger.info(f"Post {post_id} deleted")
            return True, None
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error deleting post {post_id}: {str(e)}")
            return False, "Error deleting post due to constraint violation"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting post {post_id}: {str(e)}")
            return False, str(e)

class VoteService:
    """Service class for voting operations"""
    
    @staticmethod
    def vote_post(user_id, post_id, vote_type):
        """Vote on a post (upvote=True, downvote=False)"""
        try:
            # Check if post exists
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"
            
            # Use a database transaction to handle concurrent voting
            with db.session.begin_nested():
                # Check for existing vote
                existing_vote = Vote.query.filter_by(user_id=user_id, post_id=post_id).first()
                
                if existing_vote:
                    if existing_vote.vote_type == vote_type:
                        # Same vote type - remove vote (toggle off)
                        db.session.delete(existing_vote)
                        action = "removed"
                    else:
                        # Different vote type - update vote
                        existing_vote.vote_type = vote_type
                        action = "updated"
                else:
                    # New vote
                    vote = Vote(user_id=user_id, post_id=post_id, vote_type=vote_type)
                    db.session.add(vote)
                    action = "added"
            
            db.session.commit()
            
            # Return updated post with vote counts
            post_dict = post.to_dict()
            post_dict['vote_action'] = action
            
            current_app.logger.info(f"Vote {action} for post {post_id} by user {user_id}")
            return post_dict, None
            
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error voting on post {post_id}: {str(e)}")
            return None, "Voting conflict occurred, please try again"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error voting on post {post_id}: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_user_vote_on_post(user_id, post_id):
        """Get user's vote on a specific post"""
        try:
            vote = Vote.query.filter_by(user_id=user_id, post_id=post_id).first()
            return vote, None
        except Exception as e:
            current_app.logger.error(f"Error getting user vote: {str(e)}")
            return None, str(e)

class UserService:
    """Service class for user operations"""
    
    @staticmethod
    def create_user(username, email, password):
        """Create a new user account"""
        try:
            user = User(username=username.strip(), email=email.strip())
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f"User created: {username}")
            return user, None
        except IntegrityError as e:
            db.session.rollback()
            # Handle specific constraint violations
            if 'username' in str(e.orig):
                return None, "Username already exists"
            elif 'email' in str(e.orig):
                return None, "Email already exists"
            else:
                current_app.logger.error(f"Integrity error creating user: {str(e)}")
                return None, "User already exists"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user credentials"""
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password) and user.is_active:
                return user, None
            return None, "Invalid credentials"
        except Exception as e:
            current_app.logger.error(f"Error authenticating user: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID for profile information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            return user, None
        except Exception as e:
            current_app.logger.error(f"Error fetching user {user_id}: {str(e)}")
            return None, str(e)

class CommentService:
    """Service class for comment operations"""
    
    @staticmethod
    def create_comment(content, author_id, post_id):
        """Create a new comment on a post"""
        try:
            # Check if post exists
            post = Post.query.get(post_id)
            if not post:
                return None, "Post not found"
            
            comment = Comment(
                content=content.strip(),
                author_id=author_id,
                post_id=post_id
            )
            
            db.session.add(comment)
            db.session.commit()
            
            current_app.logger.info(f"Comment created on post {post_id}")
            return comment, None
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Integrity error creating comment: {str(e)}")
            return None, "Error creating comment due to constraint violation"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating comment: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_post_comments(post_id, page=1, per_page=10):
        """Get comments for a specific post"""
        try:
            comments = Comment.query.filter_by(post_id=post_id, is_active=True)\
                                  .order_by(Comment.created_at.desc())\
                                  .paginate(page=page, per_page=per_page, error_out=False)
            return comments, None
        except Exception as e:
            current_app.logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
            return None, str(e)