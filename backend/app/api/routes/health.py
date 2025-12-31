"""Health check endpoints."""

import logging
from flask import jsonify, current_app
from datetime import datetime

from app.api import api_bp

logger = logging.getLogger(__name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    try:
        cache_service = current_app.cache_service
        cache_stats = cache_service.get_stats() if cache_service else {}
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'cache': cache_stats,
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@api_bp.route('/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint.
    
    Returns:
        Pong response
    """
    return jsonify({'message': 'pong'}), 200
