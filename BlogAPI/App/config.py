import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings"""
    # Database configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLITE_PATH = os.path.join(BASE_DIR, '..', 'blog.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f"sqlite:///{SQLITE_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    # JWT configuration for authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_LEEWAY = 10  # Allow 10 seconds of leeway for clock skew
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries in development

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    # Override with a test database file path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEST_DB_PATH = os.path.join(BASE_DIR, '..', 'tests', 'test_debug.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{TEST_DB_PATH}"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
