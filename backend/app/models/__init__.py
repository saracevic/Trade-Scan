"""
Data models for Trade-Scan application.

This module defines Pydantic models for type-safe data structures used
throughout the application.
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CoinInfo(BaseModel):
    """Basic coin information."""
    
    id: str = Field(..., description="CoinGecko coin ID")
    symbol: str = Field(..., description="Coin symbol (e.g., BTC)")
    name: str = Field(..., description="Coin full name")
    market_cap_rank: Optional[int] = Field(None, description="Market cap ranking")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "market_cap_rank": 1
            }
        }


class ATHATLData(BaseModel):
    """All-Time High and All-Time Low data."""
    
    ath: float = Field(..., description="All-time high price", gt=0)
    ath_date: Optional[datetime] = Field(None, description="ATH date")
    atl: float = Field(..., description="All-time low price", gt=0)
    atl_date: Optional[datetime] = Field(None, description="ATL date")
    current_price: float = Field(..., description="Current price", gt=0)
    
    @field_validator('atl')
    @classmethod
    def validate_atl_less_than_ath(cls, v, info):
        """Ensure ATL is less than ATH."""
        if 'ath' in info.data and v >= info.data['ath']:
            raise ValueError('ATL must be less than ATH')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "ath": 69000.0,
                "ath_date": "2021-11-10T00:00:00Z",
                "atl": 67.81,
                "atl_date": "2013-07-06T00:00:00Z",
                "current_price": 43500.0
            }
        }


class FibonacciLevel(BaseModel):
    """Single Fibonacci level."""
    
    level: float = Field(..., description="Fibonacci ratio (e.g., 0.236, 0.382)")
    price: float = Field(..., description="Price at this Fibonacci level", gt=0)
    label: str = Field(..., description="Human-readable label (e.g., '23.6%', '38.2%')")
    type: str = Field(..., description="Type: 'retracement' or 'extension'")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "level": 0.382,
                "price": 52650.3,
                "label": "38.2%",
                "type": "retracement"
            }
        }


class FibonacciAnalysis(BaseModel):
    """Complete Fibonacci analysis for a coin."""
    
    symbol: str = Field(..., description="Coin symbol")
    ath: float = Field(..., description="All-time high", gt=0)
    atl: float = Field(..., description="All-time low", gt=0)
    current_price: float = Field(..., description="Current price", gt=0)
    price_range: float = Field(..., description="ATH - ATL range", gt=0)
    retracement_levels: List[FibonacciLevel] = Field(..., description="Fibonacci retracement levels")
    extension_levels: List[FibonacciLevel] = Field(..., description="Fibonacci extension levels")
    nearest_support: Optional[FibonacciLevel] = Field(None, description="Nearest support level")
    nearest_resistance: Optional[FibonacciLevel] = Field(None, description="Nearest resistance level")
    position_percentage: float = Field(
        ..., 
        description="Current position in ATH-ATL range (0-100%)",
        ge=0,
        le=100
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "ath": 69000.0,
                "atl": 67.81,
                "current_price": 43500.0,
                "price_range": 68932.19,
                "retracement_levels": [],
                "extension_levels": [],
                "nearest_support": None,
                "nearest_resistance": None,
                "position_percentage": 62.95
            }
        }


class AsianRangeData(BaseModel):
    """Asian Range data for a coin."""
    
    symbol: str = Field(..., description="Coin symbol")
    body_high: float = Field(..., description="Body high price", gt=0)
    body_low: float = Field(..., description="Body low price", gt=0)
    fib_50: float = Field(..., description="50% Fibonacci level", gt=0)
    candle_count: int = Field(..., description="Number of candles used", gt=0)
    calculated_at: datetime = Field(..., description="Calculation timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "body_high": 44000.0,
                "body_low": 43000.0,
                "fib_50": 43500.0,
                "candle_count": 5,
                "calculated_at": "2024-01-01T00:00:00Z"
            }
        }


class CoinMarketData(BaseModel):
    """Complete market data for a coin."""
    
    symbol: str = Field(..., description="Coin symbol")
    name: str = Field(..., description="Coin name")
    current_price: float = Field(..., description="Current price", gt=0)
    price_change_24h: float = Field(..., description="24h price change percentage")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    market_cap_rank: Optional[int] = Field(None, description="Market cap rank")
    ath: Optional[float] = Field(None, description="All-time high")
    atl: Optional[float] = Field(None, description="All-time low")
    fibonacci_analysis: Optional[FibonacciAnalysis] = Field(None, description="Fibonacci analysis")
    asian_range: Optional[AsianRangeData] = Field(None, description="Asian range data")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 43500.0,
                "price_change_24h": 2.5,
                "volume_24h": 25000000000.0,
                "market_cap": 850000000000.0,
                "market_cap_rank": 1,
                "ath": 69000.0,
                "atl": 67.81,
                "fibonacci_analysis": None,
                "asian_range": None
            }
        }


class ScanResult(BaseModel):
    """Result from scanning multiple coins."""
    
    total_coins: int = Field(..., description="Total number of coins scanned")
    coins: List[CoinMarketData] = Field(..., description="List of coin data")
    timestamp: datetime = Field(..., description="Scan timestamp")
    filters_applied: Optional[Dict[str, str]] = Field(None, description="Filters applied")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "total_coins": 100,
                "coins": [],
                "timestamp": "2024-01-01T00:00:00Z",
                "filters_applied": {"min_volume": "1000000"}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error": "Coin not found",
                "status_code": 404,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
