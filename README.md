# BlogAPI - Local Setup and Testing Guide

This guide will help you set up and run the BlogAPI project locally on your machine.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+** (Check with `python --version`)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Postman** (recommended for API testing) or **curl** command line tool

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/idorvh10/BlogAPI.git
cd BlogAPI/BlogAPI
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the project root:
```bash
# Copy the example environment file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit the `.env` file with your settings:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///blog.db
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### 5. Initialize the Database
```bash
python -c "from BlogAPI.App import create_app; from BlogAPI.App.db import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### 6. Run the Application
```bash
python run.py
```

The API will be available at: `http://localhost:5000`

## Testing the API

### Option 1: Using Postman (Recommended)

#### Import the Postman Collection
1. Open Postman
2. Click "Import" → "Raw text"
3. Copy and paste the following collection:

```json
{
    "info": {
        "name": "BlogAPI Collection",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:5000"
        },
        {
            "key": "access_token",
            "value": ""
        }
    ],
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/ping",
                    "host": ["{{base_url}}"],
                    "path": ["ping"]
                }
            }
        },
        {
            "name": "Register User",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "if (pm.response.code === 201) {",
                            "    const responseJson = pm.response.json();",
                            "    pm.collectionVariables.set('access_token', responseJson.data.access_token);",
                            "}"
                        ]
                    }
                }
            ],
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"username\": \"testuser\",\n    \"email\": \"test@example.com\",\n    \"password\": \"password123\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/auth/register",
                    "host": ["{{base_url}}"],
                    "path": ["api", "auth", "register"]
                }
            }
        },
        {
            "name": "Login User",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "if (pm.response.code === 200) {",
                            "    const responseJson = pm.response.json();",
                            "    pm.collectionVariables.set('access_token', responseJson.data.access_token);",
                            "}"
                        ]
                    }
                }
            ],
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"username\": \"testuser\",\n    \"password\": \"password123\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/auth/login",
                    "host": ["{{base_url}}"],
                    "path": ["api", "auth", "login"]
                }
            }
        },
        {
            "name": "Get Current User",
            "request": {
                "method": "GET",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{access_token}}"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}/api/auth/me",
                    "host": ["{{base_url}}"],
                    "path": ["api", "auth", "me"]
                }
            }
        },
        {
            "name": "Create Post",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "key": "Authorization",
                        "value": "Bearer {{access_token}}"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"title\": \"My First Blog Post\",\n    \"body\": \"This is the content of my first blog post. It contains interesting information about the topic.\",\n    \"author\": \"Test Author\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/posts",
                    "host": ["{{base_url}}"],
                    "path": ["api", "posts"]
                }
            }
        },
        {
            "name": "Get All Posts",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/posts",
                    "host": ["{{base_url}}"],
                    "path": ["api", "posts"]
                }
            }
        },
        {
            "name": "Vote on Post",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "key": "Authorization",
                        "value": "Bearer {{access_token}}"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"vote_type\": \"upvote\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/posts/1/vote",
                    "host": ["{{base_url}}"],
                    "path": ["api", "posts", "1", "vote"]
                }
            }
        },
        {
            "name": "Search Posts",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/search?q=blog",
                    "host": ["{{base_url}}"],
                    "path": ["api", "search"],
                    "query": [
                        {
                            "key": "q",
                            "value": "blog"
                        }
                    ]
                }
            }
        }
    ]
}
```

#### Testing Workflow with Postman:
1. **Start with Health Check** - Verify the API is running
2. **Register a User** - This will automatically save the access token
3. **Create Posts** - Use the saved token to create blog posts
4. **Test Voting** - Vote on posts and see the results
5. **Search Posts** - Test the search functionality
6. **Get User Profile** - Test user endpoints


### Option 2: Running Automated Tests

Run the built-in test suite:
```bash
# Run all tests
python -m pytest BlogAPI/tests/ -v

# Run specific test file
python -m pytest BlogAPI/tests/test_auth.py -v
```

## API Endpoints Quick Reference

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Posts
- `GET /api/posts` - Get all posts (with pagination)
- `POST /api/posts` - Create new post (authenticated)
- `GET /api/posts/{id}` - Get single post
- `PUT /api/posts/{id}` - Update post (author only)
- `DELETE /api/posts/{id}` - Delete post (author only)

### Voting
- `POST /api/posts/{id}/vote` - Vote on post (authenticated)
- `GET /api/posts/{id}/vote-status` - Get user's vote status (authenticated)

### Users
- `GET /api/users/{id}` - Get user profile

### Comments
- `POST /api/posts/{id}/comments` - Create comment (authenticated)
- `GET /api/posts/{id}/comments` - Get post comments

### Search
- `GET /api/search?q=term` - Search posts

### Utility
- `GET /` - API information
- `GET /ping` - Health check

The API includes comprehensive error handling and logging to help identify issues quickly.
