import os
import logging
from logging.handlers import RotatingFileHandler
import argparse
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app import app
from config.settings import PORT, DEBUG, BASE_DIR

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Set up logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for logging
    file_handler = RotatingFileHandler(
        log_dir / 'food_app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Remove default Flask handlers and add our custom handlers
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Also log werkzeug (Flask's built-in server)
    logging.getLogger('werkzeug').handlers = []
    logging.getLogger('werkzeug').addHandler(file_handler)
    logging.getLogger('werkzeug').addHandler(console_handler)
    
    return app.logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the Food Recommendation App')
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to run the application on'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=PORT,
        help='Port to run the application on'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=DEBUG,
        help='Run the application in debug mode'
    )
    return parser.parse_args()

def init_app():
    """Initialize the application"""
    logger = setup_logging()
    logger.info('Starting Food Recommendation App...')
    
    # Ensure required directories exist
    static_dir = BASE_DIR / 'static' / 'generated_images'
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize services if needed
    # This is where you could add any additional initialization
    # such as checking database connections, warming up models, etc.
    
    logger.info('Application initialized successfully')
    return app

def main():
    """Main entry point of the application"""
    try:
        args = parse_arguments()
        app = init_app()
        
        app.logger.info(f'Running on http://{args.host}:{args.port}')
        app.logger.info(f'Debug mode: {args.debug}')
        
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except Exception as e:
        app.logger.error(f'Failed to start application: {e}', exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()