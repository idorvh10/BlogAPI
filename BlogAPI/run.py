"""
Blog Platform API - Application Entry Point
===========================================
This file starts the Flask application with proper configuration.
"""

import os
from dotenv import load_dotenv
from App import create_app

# Load environment variables from .env file
load_dotenv()

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Get configuration from environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Log startup information
    app.logger.info(f"Starting Blog Platform API on {host}:{port}")
    app.logger.info(f"Debug mode: {debug_mode}")
    app.logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )