"""
Configuration module for Trade-Scan backend.

This module provides configuration management using environment variables
with sensible defaults.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""

    # Flask Configuration
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False" if os.getenv("FLASK_ENV") == "production" else "True").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # API Configuration
    COINGECKO_API_URL: str = os.getenv(
        "COINGECKO_API_URL", 
        "https://api.coingecko.com/api/v3"
    )
    BINANCE_FUTURES_API_URL: str = os.getenv(
        "BINANCE_FUTURES_API_URL",
        "https://fapi.binance.com/fapi/v1"
    )
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # Rate Limiting
    COINGECKO_RATE_LIMIT: int = int(os.getenv("COINGECKO_RATE_LIMIT", "50"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_config(cls) -> dict:
        """
        Get all configuration as a dictionary.
        
        Returns:
            dict: Configuration key-value pairs
        """
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith("_") and key.isupper()
        }


# Create a singleton config instance
config = Config()
