"""
Application Factory
===================
This module contains the Flask application factory for creating
and configuring the blog platform application.
"""

import logging
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from .config import config
from .db import db
from .routes import register_routes

# Initialize extensions
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

def create_app(config_name=None):
    """
    Application factory function
    Creates and configures a Flask application instance
    """
    
    # Create Flask application instance
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    # Register routes
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    # Log successful application creation
    app.logger.info(f"Blog Platform API created with config: {config_name}")
    
    return app

def configure_logging(app):
    """Configure application logging"""
    # Get the absolute path to  the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(project_dir, 'logs')
    log_file = os.path.join(logs_dir, 'blog_api.log')

    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)

    # Check if FileHandler already exists to prevent duplicates
    has_file_handler = any(isinstance(handler, logging.FileHandler) for handler in app.logger.handlers)
    if not has_file_handler:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Blog API startup')

    # Optionally, also log to console in development
    if app.debug or app.testing:
        # Check if StreamHandler already exists to prevent duplicates
        has_stream_handler = any(isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler) for handler in app.logger.handlers)
        if not has_stream_handler:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            console_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(console_handler)