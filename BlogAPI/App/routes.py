"""
API Routes Layer
================
This module contains all API endpoints for the blog platform.
Routes handle HTTP requests and responses, delegating business logic to services.
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Post, User, Vote, Comment
from .services import PostService, VoteService, UserService, CommentService
from .schemas import (
    PostCreateSchema, PostUpdateSchema, PostSearchSchema, VoteSchema,
    UserRegistrationSchema, UserLoginSchema, CommentCreateSchema,
    PaginationSchema, validate_json_data, serialize_data,
    PostResponseSchema, UserResponseSchema, CommentResponseSchema
)
from .auth import jwt_required_custom, jwt_optional_custom, get_current_user, create_access_token_for_user
from .db import db

def register_routes(app):
    """Register all API routes with the Flask application"""
    
    # ============================================================================
    # UTILITY ENDPOINTS
    # ============================================================================
    
    @app.route("/")
    def home():
        """Home endpoint - API information"""
        return jsonify({
            'success': True,
            'message': 'Blog Platform API',
            'data': {
                'version': '1.0.0',
                'description': 'A scalable blog platform with authentication, voting, and search',
                'endpoints': {
                    'auth': '/api/auth/*',
                    'posts': '/api/posts/*',
                    'users': '/api/users/*',
                    'search': '/api/search'
                }
            }
        })
    
    @app.route("/ping")
    def ping():
        """Health check endpoint"""
        return jsonify({
            'success': True,
            'message': 'pong',
            'data': {'status': 'healthy'}
        })
    
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        """User registration endpoint"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'errors': {'request': 'JSON data required'}
                }), 400
            
            # Validate input data
            validated_data, errors = validate_json_data(UserRegistrationSchema, data)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400
            
            # Create user
            user, error = UserService.create_user(
                validated_data['username'],
                validated_data['email'],
                validated_data['password']
            )
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Registration failed',
                    'errors': {'registration': error}
                }), 400
            
            # Create tokens
            tokens, token_error = create_access_token_for_user(user)
            if token_error:
                return jsonify({
                    'success': False,
                    'message': 'Registration successful but token creation failed',
                    'errors': {'token': token_error}
                }), 500
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': tokens
            }), 201
            
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Registration failed'}
            }), 500
    
    @app.route("/api/auth/login", methods=["POST"])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'errors': {'request': 'JSON data required'}
                }), 400
            
            # Validate input data
            validated_data, errors = validate_json_data(UserLoginSchema, data)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400
            
            # Authenticate user
            user, error = UserService.authenticate_user(
                validated_data['username'],
                validated_data['password']
            )
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Login failed',
                    'errors': {'authentication': error}
                }), 401
            
            # Create tokens
            tokens, token_error = create_access_token_for_user(user)
            if token_error:
                return jsonify({
                    'success': False,
                    'message': 'Authentication successful but token creation failed',
                    'errors': {'token': token_error}
                }), 500
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': tokens
            })
            
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Login failed'}
            }), 500

    @app.route("/api/auth/me", methods=["GET"])
    @jwt_required_custom
    def get_current_user_info():
        """Get current user information"""
        try:
            user = get_current_user()
            return jsonify({
                'success': True,
                'message': 'User information retrieved',
                'data': serialize_data(UserResponseSchema, user)
            })
        except Exception as e:
            current_app.logger.error(f"Get user info error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve user information',
                'errors': {'server': 'Internal error'}
            }), 500
    
    # ============================================================================
    # USER ENDPOINTS
    # ============================================================================
    
    @app.route("/api/users/<int:user_id>", methods=["GET"])
    def get_user_profile(user_id):
        """Get user profile information"""
        try:
            user, error = UserService.get_user_by_id(user_id)
            if error:
                return jsonify({
                    'success': False,
                    'message': 'User not found',
                    'errors': {'user': error}
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'User profile retrieved',
                'data': serialize_data(UserResponseSchema, user)
            })
        except Exception as e:
            current_app.logger.error(f"Get user profile error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve user profile',
                'errors': {'server': 'Internal error'}
            }), 500
    
    @app.route("/api/posts/<int:post_id>/vote-status", methods=["GET"])
    @jwt_required_custom
    def get_vote_status(post_id):
        """Get current user's vote status on a post"""
        try:
            current_user = get_current_user()
            vote, error = VoteService.get_user_vote_on_post(current_user.id, post_id)
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Error retrieving vote status',
                    'errors': {'vote': error}
                }), 500
            
            vote_data = None
            if vote:
                vote_data = {
                    'vote_type': 'upvote' if vote.vote_type else 'downvote',
                    'created_at': vote.created_at.isoformat()
                }
            
            return jsonify({
                'success': True,
                'message': 'Vote status retrieved',
                'data': {
                    'has_voted': vote is not None,
                    'vote': vote_data
                }
            })
        except Exception as e:
            current_app.logger.error(f"Get vote status error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve vote status',
                'errors': {'server': 'Internal error'}
            }), 500
    
    # ============================================================================
    # POST MANAGEMENT ENDPOINTS
    # ============================================================================
    
    @app.route("/api/posts", methods=["POST"])
    @jwt_required_custom
    def create_post():
        """Create a new blog post"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'errors': {'request': 'JSON data required'}
                }), 400
            
            # Validate input data
            validated_data, errors = validate_json_data(PostCreateSchema, data)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400
            
            # Get current user
            current_user = get_current_user()
            
            # Create post
            post, error = PostService.create_post(
                validated_data['title'],
                validated_data['body'],
                validated_data['author'],
                current_user.id
            )
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create post',
                    'errors': {'creation': error}
                }), 400
            
            return jsonify({
                'success': True,
                'message': 'Post created successfully',
                'data': serialize_data(PostResponseSchema, post)
            }), 201
            
        except Exception as e:
            current_app.logger.error(f"Create post error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Post creation failed'}
            }), 500
    
    @app.route("/api/posts", methods=["GET"])
    @jwt_optional_custom
    def list_posts():
        """Get paginated list of posts with optional sorting"""
        try:
            # Validate query parameters
            args = request.args.to_dict()
            validated_args, errors = validate_json_data(PostSearchSchema, args)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Invalid query parameters',
                    'errors': errors
                }), 400
            
            # Get posts
            posts_pagination, error = PostService.get_all_posts(
                page=validated_args['page'],
                per_page=validated_args['per_page'],
                sort_by=validated_args['sort_by'],
                order=validated_args['order']
            )
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Failed to retrieve posts',
                    'errors': {'retrieval': error}
                }), 500
            
            return jsonify({
                'success': True,
                'message': 'Posts retrieved successfully',
                'data': serialize_data(PostResponseSchema, posts_pagination.items, many=True),
                'pagination': {
                    'page': posts_pagination.page,
                    'pages': posts_pagination.pages,
                    'per_page': posts_pagination.per_page,
                    'total': posts_pagination.total,
                    'has_next': posts_pagination.has_next,
                    'has_prev': posts_pagination.has_prev
                }
            })
            
        except Exception as e:
            current_app.logger.error(f"List posts error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Failed to retrieve posts'}
            }), 500
    
    @app.route("/api/posts/<int:post_id>", methods=["GET"])
    @jwt_optional_custom
    def get_post(post_id):
        """Get a single post by ID"""
        try:
            post, error = PostService.get_post_by_id(post_id)
            if error:
                return jsonify({
                    'success': False,
                    'message': error,
                    'errors': {'post': error}
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Post retrieved successfully',
                'data': serialize_data(PostResponseSchema, post)
            })
            
        except Exception as e:
            current_app.logger.error(f"Get post error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Failed to retrieve post'}
            }), 500
    
    @app.route("/api/posts/<int:post_id>", methods=["PUT"])
    @jwt_required_custom
    def update_post(post_id):
        """Update an existing post (author only)"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'errors': {'request': 'JSON data required'}
                }), 400
            
            # Validate input data
            validated_data, errors = validate_json_data(PostUpdateSchema, data)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400
            
            # Check if post exists and user is author
            post, error = PostService.get_post_by_id(post_id)
            if error:
                return jsonify({
                    'success': False,
                    'message': error,
                    'errors': {'post': error}
                }), 404
            
            current_user = get_current_user()
            if post.author_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'Unauthorized to update this post',
                    'errors': {'authorization': 'Not post author'}
                }), 403
            
            # Update post
            updated_post, update_error = PostService.update_post(
                post_id,
                validated_data.get('title'),
                validated_data.get('body'),
                current_user.id
            )
            
            if update_error:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update post',
                    'errors': {'update': update_error}
                }), 400
            
            return jsonify({
                'success': True,
                'message': 'Post updated successfully',
                'data': serialize_data(PostResponseSchema, updated_post)
            })
            
        except Exception as e:
            current_app.logger.error(f"Update post error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Post update failed'}
            }), 500
    
    @app.route("/api/posts/<int:post_id>", methods=["DELETE"])
    @jwt_required_custom
    def delete_post(post_id):
        """Delete a post (author only)"""
        try:
            current_user = get_current_user()
            success, error = PostService.delete_post(post_id, current_user.id)
            
            if not success:
                if error == "Post not found":
                    return jsonify({
                        'success': False,
                        'message': error,
                        'errors': {'post': error}
                    }), 404
                else:
                    return jsonify({
                        'success': False,
                        'message': error,
                        'errors': {'authorization': error}
                    }), 403
            
            return jsonify({
                'success': True,
                'message': 'Post deleted successfully',
                'data': None
            })
            
        except Exception as e:
            current_app.logger.error(f"Delete post error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Post deletion failed'}
            }), 500
    
    # ============================================================================
    # SEARCH ENDPOINTS
    # ============================================================================
    
    @app.route("/api/search", methods=["GET"])
    @jwt_optional_custom
    def search_posts():
        """Search posts by title and content"""
        try:
            # Validate query parameters
            args = request.args.to_dict()
            validated_args, errors = validate_json_data(PostSearchSchema, args)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Invalid query parameters',
                    'errors': errors
                }), 400
            
            # Search posts
            posts_pagination, error = PostService.search_posts(
                validated_args['q'],
                validated_args['page'],
                validated_args['per_page']
            )
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Search failed',
                    'errors': {'search': error}
                }), 500
            
            return jsonify({
                'success': True,
                'message': f'Search completed for: "{validated_args["q"]}"',
                'data': serialize_data(PostResponseSchema, posts_pagination.items, many=True),
                'pagination': {
                    'page': posts_pagination.page,
                    'pages': posts_pagination.pages,
                    'per_page': posts_pagination.per_page,
                    'total': posts_pagination.total,
                    'has_next': posts_pagination.has_next,
                    'has_prev': posts_pagination.has_prev
                },
                'search_query': validated_args['q']
            })
            
        except Exception as e:
            current_app.logger.error(f"Search error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Search failed'}
            }), 500
    
    # ============================================================================
    # VOTING ENDPOINTS
    # ============================================================================
    
    @app.route("/api/posts/<int:post_id>/vote", methods=["POST"])
    @jwt_required_custom
    def vote_on_post(post_id):
        """Vote on a post (upvote or downvote)"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'errors': {'request': 'JSON data required'}
                }), 400
            
            # Validate input data
            validated_data, errors = validate_json_data(VoteSchema, data)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400
            
            current_user = get_current_user()
            vote_type = validated_data['vote_type'] == 'upvote'
            
            # Process vote
            result, error = VoteService.vote_post(current_user.id, post_id, vote_type)
            if error:
                if error == "Post not found":
                    return jsonify({
                        'success': False,
                        'message': error,
                        'errors': {'post': error}
                    }), 404
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Vote failed',
                        'errors': {'vote': error}
                    }), 400
            
            return jsonify({
                'success': True,
                'message': f'Vote {result["vote_action"]} successfully',
                'data': result
            })
            
        except Exception as e:
            current_app.logger.error(f"Vote error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Vote failed'}
            }), 500
    
    # ============================================================================
    # COMMENT ENDPOINTS
    # ============================================================================
    
    @app.route("/api/posts/<int:post_id>/comments", methods=["POST"])
    @jwt_required_custom
    def create_comment(post_id):
        """Create a comment on a post"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided',
                    'errors': {'request': 'JSON data required'}
                }), 400
            
            # Validate input data
            validated_data, errors = validate_json_data(CommentCreateSchema, data)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': errors
                }), 400
            
            current_user = get_current_user()
            
            # Create comment
            comment, error = CommentService.create_comment(
                validated_data['content'],
                current_user.id,
                post_id
            )
            
            if error:
                if error == "Post not found":
                    return jsonify({
                        'success': False,
                        'message': error,
                        'errors': {'post': error}
                    }), 404
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create comment',
                        'errors': {'creation': error}
                    }), 400
            
            return jsonify({
                'success': True,
                'message': 'Comment created successfully',
                'data': comment.to_dict()
            }), 201
            
        except Exception as e:
            current_app.logger.error(f"Create comment error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Comment creation failed'}
            }), 500
    
    @app.route("/api/posts/<int:post_id>/comments", methods=["GET"])
    @jwt_optional_custom
    def get_post_comments(post_id):
        """Get comments for a specific post"""
        try:
            # Validate query parameters
            args = request.args.to_dict()
            validated_args, errors = validate_json_data(PaginationSchema, args)
            if errors:
                return jsonify({
                    'success': False,
                    'message': 'Invalid query parameters',
                    'errors': errors
                }), 400
            
            # Get comments
            comments_pagination, error = CommentService.get_post_comments(
                post_id,
                validated_args['page'],
                validated_args['per_page']
            )
            
            if error:
                return jsonify({
                    'success': False,
                    'message': 'Failed to retrieve comments',
                    'errors': {'retrieval': error}
                }), 500
            
            return jsonify({
                'success': True,
                'message': 'Comments retrieved successfully',
                'data': serialize_data(CommentResponseSchema, comments_pagination.items, many=True),
                'pagination': {
                    'page': comments_pagination.page,
                    'pages': comments_pagination.pages,
                    'per_page': comments_pagination.per_page,
                    'total': comments_pagination.total,
                    'has_next': comments_pagination.has_next,
                    'has_prev': comments_pagination.has_prev
                }
            })
            
        except Exception as e:
            current_app.logger.error(f"Get comments error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'errors': {'server': 'Failed to retrieve comments'}
            }), 500
    
    # ============================================================================
    # ERROR HANDLERS
    # ============================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'errors': {'route': 'Endpoint not found'}
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify({
            'success': False,
            'message': 'Method not allowed',
            'errors': {'method': 'HTTP method not supported for this endpoint'}
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': {'server': 'An unexpected error occurred'}
        }), 500
