"""
Test Configuration
==================
Configuration and fixtures for testing the blog platform API.
"""

import pytest
import os
from BlogAPI.App import create_app
from BlogAPI.App.db import db
from BlogAPI.App.models import User, Post

@pytest.fixture
def app():
    """Create and configure a test application instance"""
    import os

    # Create app with testing configuration
    app = create_app('testing')
    app.config['TESTING'] = True

    with app.app_context():
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Create authentication headers for testing"""
    # Create a test user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    
    # Register user
    response = client.post('/api/auth/register', json=user_data)
    assert response.status_code == 201
    
    data = response.get_json()
    token = data['data']['access_token']
    
    return {'Authorization': f'Bearer {token}'}

class AuthActions:
    """Helper class for authentication actions in tests"""
    
    def __init__(self, client):
        self._client = client
    
    def register(self, username='testuser', email='test@example.com', password='testpassword123'):
        """Register a new user"""
        return self._client.post('/api/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })
    
    def login(self, username='testuser', password='testpassword123'):
        """Login a user"""
        return self._client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
    
    def get_auth_headers(self, username='testuser', password='testpassword123'):
        """Get authorization headers for a user"""
        response = self.login(username, password)
        if response.status_code == 200:
            data = response.get_json()
            token = data['data']['access_token']
            return {'Authorization': f'Bearer {token}'}
        return None

@pytest.fixture
def auth(client):
    """Authentication helper fixture"""
    return AuthActions(client)