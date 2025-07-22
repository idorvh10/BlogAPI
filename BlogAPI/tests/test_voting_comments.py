"""
Voting and Comments Tests
========================
Test cases for voting and commenting functionality.
"""

import pytest
from BlogAPI.App.models import Vote, Comment

class TestVoting:
    """Test class for voting functionality"""
    
    def test_upvote_post_success(self, client, auth):
        """Test successful upvoting of a post"""
        # Create a post
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Post to Upvote',
            'body': 'This post will receive an upvote.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Upvote the post
        vote_data = {'vote_type': 'upvote'}
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['upvotes'] == 1
        assert data['data']['downvotes'] == 0
    
    def test_downvote_post_success(self, client, auth):
        """Test successful downvoting of a post"""
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Post to Downvote',
            'body': 'This post will receive a downvote.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Downvote the post
        vote_data = {'vote_type': 'downvote'}
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['upvotes'] == 0
        assert data['data']['downvotes'] == 1
    
    def test_vote_toggle_functionality(self, client, auth):
        """Test vote toggling (remove vote by voting again)"""
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Toggle Vote Post',
            'body': 'Testing vote toggling functionality.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # First upvote
        vote_data = {'vote_type': 'upvote'}
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        assert response.get_json()['data']['upvotes'] == 1
        
        # Second upvote (should remove the vote)
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        assert response.get_json()['data']['upvotes'] == 0
    
    def test_vote_change_type(self, client, auth):
        """Test changing vote type from upvote to downvote"""
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Change Vote Type Post',
            'body': 'Testing vote type changing functionality.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # First upvote
        vote_data = {'vote_type': 'upvote'}
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        assert response.get_json()['data']['upvotes'] == 1
        
        # Change to downvote
        vote_data = {'vote_type': 'downvote'}
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        data = response.get_json()['data']
        assert data['upvotes'] == 0
        assert data['downvotes'] == 1
    
    def test_vote_without_authentication(self, client, auth):
        """Test voting without authentication"""
        # Create a post
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Public Post',
            'body': 'This post cannot be voted on without auth.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Try to vote without headers
        vote_data = {'vote_type': 'upvote'}
        response = client.post(f'/api/posts/{post_id}/vote', json=vote_data)
        assert response.status_code == 401
    
    def test_vote_nonexistent_post(self, client, auth):
        """Test voting on non-existent post"""
        auth.register()
        headers = auth.get_auth_headers()
        
        vote_data = {'vote_type': 'upvote'}
        response = client.post('/api/posts/999/vote', json=vote_data, headers=headers)
        assert response.status_code == 404
    
    def test_get_vote_status_after_voting(self, client, auth):
        """Test getting vote status after voting on a post"""
        # Create a post
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Vote Status Test',
            'body': 'Testing vote status retrieval.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Vote on the post
        vote_data = {'vote_type': 'upvote'}
        client.post(f'/api/posts/{post_id}/vote', json=vote_data, headers=headers)
        
        # Check vote status
        response = client.get(f'/api/posts/{post_id}/vote-status', headers=headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['has_voted'] is True
        assert data['data']['vote']['vote_type'] == 'upvote'
    
    def test_get_vote_status_no_vote(self, client, auth):
        """Test getting vote status when user hasn't voted"""
        # Create a post
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'No Vote Test',
            'body': 'Testing vote status when no vote exists.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Check vote status without voting
        response = client.get(f'/api/posts/{post_id}/vote-status', headers=headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['has_voted'] is False
        assert data['data']['vote'] is None

class TestComments:
    """Test class for commenting functionality"""
    
    def test_create_comment_success(self, client, auth):
        """Test successful comment creation"""
        # Create a post first
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Post for Comments',
            'body': 'This post will receive comments.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Create a comment
        comment_data = {
            'content': 'This is a test comment on the post.'
        }
        
        response = client.post(f'/api/posts/{post_id}/comments', json=comment_data, headers=headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['content'] == 'This is a test comment on the post.'
        assert data['data']['author_username'] == 'testuser'
    
    def test_create_comment_without_auth(self, client, auth):
        """Test comment creation without authentication"""
        # Create a post first
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Public Post',
            'body': 'This post cannot be commented on without auth.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Try to comment without authentication
        comment_data = {'content': 'Unauthorized comment'}
        response = client.post(f'/api/posts/{post_id}/comments', json=comment_data)
        assert response.status_code == 401
    
    def test_create_comment_on_nonexistent_post(self, client, auth):
        """Test commenting on non-existent post"""
        auth.register()
        headers = auth.get_auth_headers()
        
        comment_data = {'content': 'Comment on non-existent post'}
        response = client.post('/api/posts/999/comments', json=comment_data, headers=headers)
        assert response.status_code == 404
    
    def test_get_post_comments_success(self, client, auth):
        """Test getting comments for a post"""
        # Create a post and comments
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Post with Comments',
            'body': 'This post will have multiple comments.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Create multiple comments
        for i in range(3):
            comment_data = {'content': f'This is comment number {i+1}'}
            client.post(f'/api/posts/{post_id}/comments', json=comment_data, headers=headers)
        
        # Get comments
        response = client.get(f'/api/posts/{post_id}/comments')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        assert 'pagination' in data
    
    def test_comment_validation(self, client, auth):
        """Test comment validation"""
        # Create a post first
        auth.register()
        headers = auth.get_auth_headers()
        
        post_data = {
            'title': 'Validation Test Post',
            'body': 'Testing comment validation.',
            'author': 'Test Author'
        }
        
        create_response = client.post('/api/posts', json=post_data, headers=headers)
        post_id = create_response.get_json()['data']['id']
        
        # Test empty content
        comment_data = {'content': ''}
        response = client.post(f'/api/posts/{post_id}/comments', json=comment_data, headers=headers)
        assert response.status_code == 400
        
        # Test missing content
        response = client.post(f'/api/posts/{post_id}/comments', json={}, headers=headers)
        assert response.status_code == 400