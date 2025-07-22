"""
Authentication Utilities
========================
This module contains authentication helpers and decorators.
Handles JWT token creation, validation, and user authorization.
"""

from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity, 
    verify_jwt_in_request,
    get_jwt
)
from .models import User

def create_access_token_for_user(user):
    """Create access token for a user"""
    try:
        # Ensure user.id is a string for JWT 'sub' claim
        identity = str(user.id)
        access_token = create_access_token(identity=identity)
        
        return {
            'access_token': access_token,
            'user': user.to_dict()
        }, None
    except Exception as e:
        current_app.logger.error(f"JWT creation error: {str(e)}")
        return None, str(e)

def jwt_required_custom(f):
    """
    Custom JWT required decorator that provides better error handling
    and user information
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token is present and valid
            verify_jwt_in_request()
            
            # Get current user ID from token
            current_user_id = get_jwt_identity()
            
            # Fetch user from database
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'User not found or inactive',
                    'errors': {'auth': 'Invalid user'}
                }), 401
            
            # Add user to request context
            request.current_user = user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"JWT validation error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Authentication failed',
                'errors': {'auth': 'Invalid or expired token'}
            }), 401
    
    return decorated_function

def jwt_optional_custom(f):
    """
    Custom JWT optional decorator that adds user info if token is present
    but doesn't require authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if Authorization header is present
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                verify_jwt_in_request(optional=True)
                current_user_id = get_jwt_identity()
                
                if current_user_id:
                    user = User.query.get(current_user_id)
                    if user and user.is_active:
                        request.current_user = user
                    else:
                        request.current_user = None
                else:
                    request.current_user = None
            else:
                request.current_user = None
            
            return f(*args, **kwargs)
            
        except Exception as e:
            # If JWT validation fails in optional mode, continue without user
            current_app.logger.warning(f"JWT optional validation warning: {str(e)}")
            request.current_user = None
            return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(request, 'current_user', None)