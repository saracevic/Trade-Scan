"""API routes package initialization."""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import routes to register them with the blueprint
from app.api.routes import coins, health

__all__ = ['api_bp']
