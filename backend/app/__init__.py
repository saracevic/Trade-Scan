"""Flask application initialization and configuration."""

import logging
from flask import Flask
from flask_cors import CORS

from app.config import config
from app.services import (
    get_cache_service,
    CoinGeckoService,
    FibonacciService,
    ScannerService
)
from app.api import api_bp


def setup_logging():
    """Configure application logging."""
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    logger.info("Initializing services...")
    
    # Initialize services
    cache_service = get_cache_service(
        ttl=config.CACHE_TTL,
        max_size=config.CACHE_MAX_SIZE
    )
    
    coingecko_service = CoinGeckoService(cache_service=cache_service)
    fibonacci_service = FibonacciService()
    
    scanner_service = ScannerService(
        coingecko_service=coingecko_service,
        fibonacci_service=fibonacci_service,
        cache_service=cache_service
    )
    
    # Store services in app context for access in routes
    app.cache_service = cache_service
    app.coingecko_service = coingecko_service
    app.fibonacci_service = fibonacci_service
    app.scanner_service = scanner_service
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    logger.info("Application initialized successfully")
    
    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint with API information."""
        return {
            'name': 'Trade-Scan API',
            'version': '1.0.0',
            'description': 'Professional cryptocurrency analysis with Fibonacci levels',
            'endpoints': {
                'health': '/api/v1/health',
                'coins': '/api/v1/coins',
                'coin_detail': '/api/v1/coins/{symbol}',
                'fibonacci': '/api/v1/coins/{symbol}/fibonacci',
                'ath_atl': '/api/v1/coins/{symbol}/ath-atl',
                'scan': '/api/v1/scan'
            }
        }
    
    return app
