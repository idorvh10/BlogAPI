"""
Post Management Tests
====================
Test cases for blog post CRUD operations and search functionality.
"""

import pytest
from BlogAPI.App.models import Post

class TestPosts:
    """Test class for post management endpoints"""
    
    def test_create_post_success(self, client, auth):
        """Test successful post creation"""
        # Register and get auth headers
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Test Post Title',
            'body': 'This is a test post with enough content to pass validation.',
            'author': 'Test Author'
        }
        
        response = client.post('/api/posts', json=post_data, headers=headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['title'] == 'Test Post Title'
        assert data['data']['author'] == 'Test Author'
    
    def test_create_post_without_auth(self, client):
        """Test post creation without authentication"""
        post_data = {
            'title': 'Test Post',
            'body': 'This should fail without authentication.',
            'author': 'Test Author'
        }
        
        response = client.post('/api/posts', json=post_data)
        assert response.status_code == 401
    
    def test_create_post_invalid_data(self, client, auth):
        """Test post creation with invalid data"""
        auth.register()
        headers = auth.get_auth_headers()
        
        # Test missing title
        post_data = {
            'body': 'Content without title',
            'author': 'Test Author'
        }
        response = client.post('/api/posts', json=post_data, headers=headers)
        assert response.status_code == 400
        
        # Test short body
        post_data = {
            'title': 'Test Title',
            'body': 'Short',
            'author': 'Test Author'
        }
        response = client.post('/api/posts', json=post_data, headers=headers)
        assert response.status_code == 400
    
    def test_list_posts_success(self, client, auth):
        """Test listing posts"""
        # Create some posts first
        auth.register()
        headers = auth.get_auth_headers()
        
        for i in range(3):
            post_data = {
                'title': f'Test Post {i+1}',
                'body': f'This is test post number {i+1} with sufficient content.',
                'author': 'Test Author'
            }
            client.post('/api/posts', json=post_data, headers=headers)
        
        # List posts
        response = client.get('/api/posts')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        assert 'pagination' in data
    
    def test_get_single_post_success(self, client, auth):
        """Test getting a single post"""
        # Create a post first
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Single Post Test',
            'body': 'This is a single post for testing retrieval.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Get the post
        response = client.get(f'/api/posts/{post_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['title'] == 'Single Post Test'
    
    def test_get_nonexistent_post(self, client):
        """Test getting a non-existent post"""
        response = client.get('/api/posts/999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_post_success(self, client, auth):
        """Test successful post update"""
        # Create a post first
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Original Title',
            'body': 'Original content that will be updated later.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Update the post
        update_data = {
            'title': 'Updated Title',
            'body': 'This content has been updated with new information.'
        }
        
        response = client.put(f'/api/posts/{post_id}', json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['title'] == 'Updated Title'
    
    def test_update_post_unauthorized(self, client, auth):
        """Test updating post by non-author"""
        # Create a post with first user
        auth.register('user1', 'user1@example.com')
        headers1 = auth.get_auth_headers('user1')
        
        post_data = {
            'title': 'User 1 Post',
            'body': 'This post belongs to user 1 and should not be editable by others.',
            'author': 'User 1'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers1)
        post_id = create_response.get_json()['data']['id']
        
        # Try to update with different user
        auth.register('user2', 'user2@example.com')
        headers2 = auth.get_auth_headers('user2')
        
        update_data = {'title': 'Hacked Title'}
        response = client.put(f'/api/posts/{post_id}', json=update_data, headers=headers2)
        assert response.status_code == 403
    
    def test_delete_post_success(self, client, auth):
        """Test successful post deletion"""
        # Create a post first
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Post to Delete',
            'body': 'This post will be deleted in the test.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Delete the post
        response = client.delete(f'/api/posts/{post_id}', headers=headers)
        assert response.status_code == 200
        
        # Verify post is deleted
        get_response = client.get(f'/api/posts/{post_id}')
        assert get_response.status_code == 404
    
    def test_search_posts_success(self, client, auth):
        """Test post search functionality"""
        # Create posts with different content
        auth.register()
        headers = auth.get_auth_headers()
        
        posts_data = [
            {'title': 'Test Title 1', 'body': 'This is the body of test post 1.'},
            {'title': 'Test Title 2', 'body': 'This is the body of test post 2.'},
            {'title': 'Test Title 3', 'body': 'This is the body of test post 3.'}
        ]
        
        for post_data in posts_data:
            post_data['author'] = 'Test Author'
            client.post('/api/posts', json=post_data, headers=headers)
        
        # Search for "Title 2" in posts
        response = client.get('/api/search?q=Title 2')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1  # Only one post contains "Title 2"
        assert data['search_query'] == 'Title 2'
    
    def test_search_posts_empty_query(self, client, auth):
        """Test search with empty query returns all posts"""
        # Create a post
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Test Post',
            'body': 'This is a test post for empty search.',
            'author': 'Test Author'
        }
        client.post('/api/posts', json=post_data, headers=headers)
        
        # Search with empty query
        response = client.get('/api/search?q=')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1