"""Main entry point for Trade-Scan backend application."""

import logging
from app import create_app
from app.config import config

logger = logging.getLogger(__name__)


def main():
    """Start the Flask application."""
    app = create_app()
    
    logger.info(
        f"Starting Trade-Scan API server on {config.HOST}:{config.PORT} "
        f"(debug={config.DEBUG})"
    )
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


if __name__ == '__main__':
    main()
