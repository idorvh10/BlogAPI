"""
Authentication Tests
====================
Test cases for user authentication functionality.
"""

import pytest
from BlogAPI.App.models import User

class TestAuthentication:
    """Test class for authentication endpoints"""
    
    def test_user_registration_success(self, client):
        """Test successful user registration"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['user']['username'] == 'newuser'
    
    def test_user_registration_duplicate_username(self, client, auth):
        """Test registration with duplicate username"""
        # Register first user
        auth.register()
        
        # Try to register with same username
        user_data = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert 'Username already exists' in data['errors']['registration']
    
    def test_user_registration_invalid_data(self, client):
        """Test registration with invalid data"""
        # Test missing required fields
        response = client.post('/api/auth/register', json={})
        assert response.status_code == 400
        
        # Test invalid email
        user_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123'
        }
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
        
        # Test short password
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123'
        }
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
    
    def test_user_login_success(self, client, auth):
        """Test successful user login"""
        # Register user first
        auth.register()
        
        # Login
        response = auth.login()
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
    
    def test_user_login_invalid_credentials(self, client, auth):
        """Test login with invalid credentials"""
        # Register user first
        auth.register()
        
        # Try login with wrong password
        response = auth.login(password='wrongpassword')
        assert response.status_code == 401
        
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid credentials' in data['errors']['authentication']
    
    def test_get_current_user_info(self, client, auth):
        """Test getting current user information"""
        # Register and get auth headers
        auth.register()
        headers = auth.get_auth_headers()
        
        response = client.get('/api/auth/me', headers=headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token"""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_user_profile(self, client, auth):
        """Test getting user profile by ID"""
        # Register and get user
        auth.register()
        
        response = client.get('/api/users/1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
    
    def test_get_nonexistent_user_profile(self, client):
        """Test getting profile of nonexistent user"""
        response = client.get('/api/users/999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False