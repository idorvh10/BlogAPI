"""
Validation Schemas
==================
This module contains validation schemas for API requests and responses.
Using marshmallow for data validation and serialization.
"""

from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    """Schema for user registration validation"""
    username = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=3, max=80),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Username can only contain letters, numbers, and underscores")
        ]
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
        load_only=True  # Don't include in serialized output
    )

class UserLoginSchema(Schema):
    """Schema for user login validation"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class PostCreateSchema(Schema):
    """Schema for post creation validation"""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Title is required'}
    )
    body = fields.Str(
        required=True,
        validate=validate.Length(min=10),
        error_messages={'required': 'Body is required'}
    )
    author = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Author is required'}
    )

class PostUpdateSchema(Schema):
    """Schema for post update validation"""
    title = fields.Str(
        validate=validate.Length(min=1, max=200),
        load_default=None
    )
    body = fields.Str(
        validate=validate.Length(min=10),
        load_default=None
    )

class PostSearchSchema(Schema):
    """Schema for post search parameters"""
    q = fields.Str(load_default="")  # Search query
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(
        load_default="published_at",
        validate=validate.OneOf(['published_at', 'title', 'vote_score'])
    )
    order = fields.Str(
        load_default="desc",
        validate=validate.OneOf(['asc', 'desc'])
    )

class VoteSchema(Schema):
    """Schema for voting validation"""
    vote_type = fields.Str(
        required=True,
        validate=validate.OneOf(['upvote', 'downvote']),
        error_messages={'required': 'Vote type is required'}
    )

class CommentCreateSchema(Schema):
    """Schema for comment creation validation"""
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000),
        error_messages={'required': 'Comment content is required'}
    )

class PaginationSchema(Schema):
    """Schema for pagination parameters"""
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))

# Response schemas for consistent API responses
class PostResponseSchema(Schema):
    """Schema for post response serialization"""
    id = fields.Int()
    title = fields.Str()
    body = fields.Str()
    author = fields.Str()
    author_id = fields.Int(allow_none=True)
    published_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')
    upvotes = fields.Int()
    downvotes = fields.Int()
    vote_score = fields.Int()
    comment_count = fields.Int()
    is_published = fields.Bool()

class UserResponseSchema(Schema):
    """Schema for user response serialization"""
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()
    created_at = fields.DateTime(format='iso')
    is_active = fields.Bool()

class CommentResponseSchema(Schema):
    """Schema for comment response serialization"""
    id = fields.Int()
    content = fields.Str()
    author_id = fields.Int()
    author_username = fields.Str()
    post_id = fields.Int()
    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')
    is_active = fields.Bool()

class ApiResponseSchema(Schema):
    """Schema for standardized API responses"""
    success = fields.Bool()
    message = fields.Str()
    data = fields.Raw(allow_none=True)
    errors = fields.Raw(allow_none=True)
    pagination = fields.Raw(allow_none=True)

# Utility functions for validation
def validate_json_data(schema_class, data):
    """
    Validate JSON data against a schema
    Returns: (validated_data, errors)
    """
    schema = schema_class()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages

def serialize_data(schema_class, data, many=False):
    """
    Serialize data using a schema
    Returns: serialized_data
    """
    schema = schema_class()
    return schema.dump(data, many=many)