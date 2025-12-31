"""
Fibonacci service for Trade-Scan application.

This module provides Fibonacci retracement and extension calculations
based on ATH/ATL values and Asian Range data.
"""

from typing import List, Optional, Tuple
from datetime import datetime
import logging

from app.models import (
    FibonacciLevel, 
    FibonacciAnalysis, 
    AsianRangeData,
    ATHATLData
)

logger = logging.getLogger(__name__)


class FibonacciService:
    """
    Service for calculating Fibonacci levels.
    
    This service provides methods to calculate Fibonacci retracement and
    extension levels based on ATH/ATL values.
    """
    
    # Standard Fibonacci ratios
    RETRACEMENT_LEVELS = [
        (0.0, "0%"),
        (0.236, "23.6%"),
        (0.382, "38.2%"),
        (0.5, "50%"),
        (0.618, "61.8%"),
        (0.786, "78.6%"),
        (1.0, "100%")
    ]
    
    EXTENSION_LEVELS = [
        (1.272, "127.2%"),
        (1.618, "161.8%"),
        (2.618, "261.8%"),
        (4.236, "423.6%")
    ]
    
    def __init__(self):
        """Initialize the Fibonacci service."""
        logger.info("FibonacciService initialized")
    
    def calculate_retracement_levels(
        self, 
        ath: float, 
        atl: float
    ) -> List[FibonacciLevel]:
        """
        Calculate Fibonacci retracement levels from ATH to ATL.
        
        Retracement levels are calculated from the ATH (All-Time High) going
        down towards the ATL (All-Time Low). These levels represent potential
        support levels during a downtrend.
        
        Args:
            ath: All-time high price
            atl: All-time low price
            
        Returns:
            List of Fibonacci retracement levels
            
        Raises:
            ValueError: If ATH <= ATL or if values are invalid
        """
        if ath <= 0 or atl <= 0:
            raise ValueError("ATH and ATL must be positive values")
        
        if ath <= atl:
            raise ValueError("ATH must be greater than ATL")
        
        price_range = ath - atl
        levels = []
        
        for ratio, label in self.RETRACEMENT_LEVELS:
            price = ath - (price_range * ratio)
            levels.append(
                FibonacciLevel(
                    level=ratio,
                    price=round(price, 8),
                    label=label,
                    type="retracement"
                )
            )
        
        logger.debug(f"Calculated {len(levels)} retracement levels for ATH={ath}, ATL={atl}")
        return levels
    
    def calculate_extension_levels(
        self, 
        ath: float, 
        atl: float
    ) -> List[FibonacciLevel]:
        """
        Calculate Fibonacci extension levels from ATL.
        
        Extension levels are calculated beyond the ATH, representing potential
        resistance levels during an uptrend that exceeds previous highs.
        
        Args:
            ath: All-time high price
            atl: All-time low price
            
        Returns:
            List of Fibonacci extension levels
            
        Raises:
            ValueError: If ATH <= ATL or if values are invalid
        """
        if ath <= 0 or atl <= 0:
            raise ValueError("ATH and ATL must be positive values")
        
        if ath <= atl:
            raise ValueError("ATH must be greater than ATL")
        
        price_range = ath - atl
        levels = []
        
        for ratio, label in self.EXTENSION_LEVELS:
            price = ath + (price_range * (ratio - 1))
            levels.append(
                FibonacciLevel(
                    level=ratio,
                    price=round(price, 8),
                    label=label,
                    type="extension"
                )
            )
        
        logger.debug(f"Calculated {len(levels)} extension levels for ATH={ath}, ATL={atl}")
        return levels
    
    def find_nearest_levels(
        self, 
        current_price: float,
        retracement_levels: List[FibonacciLevel],
        extension_levels: List[FibonacciLevel]
    ) -> Tuple[Optional[FibonacciLevel], Optional[FibonacciLevel]]:
        """
        Find nearest support and resistance levels.
        
        Args:
            current_price: Current price
            retracement_levels: List of retracement levels
            extension_levels: List of extension levels
            
        Returns:
            Tuple of (nearest_support, nearest_resistance)
        """
        all_levels = retracement_levels + extension_levels
        
        # Sort by price
        all_levels.sort(key=lambda x: x.price)
        
        nearest_support = None
        nearest_resistance = None
        
        for level in all_levels:
            if level.price < current_price:
                nearest_support = level
            elif level.price > current_price and nearest_resistance is None:
                nearest_resistance = level
                break
        
        return nearest_support, nearest_resistance
    
    def calculate_position_percentage(
        self, 
        current_price: float, 
        ath: float, 
        atl: float
    ) -> float:
        """
        Calculate current price position in ATH-ATL range.
        
        Returns a percentage (0-100) indicating where the current price is
        positioned between ATL (0%) and ATH (100%).
        
        Args:
            current_price: Current price
            ath: All-time high price
            atl: All-time low price
            
        Returns:
            Position percentage (0-100)
        """
        if ath <= atl:
            return 0.0
        
        price_range = ath - atl
        position = current_price - atl
        percentage = (position / price_range) * 100
        
        # Clamp between 0 and 100
        return max(0.0, min(100.0, round(percentage, 2)))
    
    def analyze(
        self, 
        symbol: str,
        ath_atl_data: ATHATLData
    ) -> FibonacciAnalysis:
        """
        Perform complete Fibonacci analysis for a coin.
        
        Args:
            symbol: Coin symbol
            ath_atl_data: ATH/ATL data object
            
        Returns:
            Complete Fibonacci analysis
            
        Raises:
            ValueError: If data is invalid
        """
        ath = ath_atl_data.ath
        atl = ath_atl_data.atl
        current_price = ath_atl_data.current_price
        
        # Calculate retracement and extension levels
        retracement_levels = self.calculate_retracement_levels(ath, atl)
        extension_levels = self.calculate_extension_levels(ath, atl)
        
        # Find nearest support and resistance
        nearest_support, nearest_resistance = self.find_nearest_levels(
            current_price,
            retracement_levels,
            extension_levels
        )
        
        # Calculate position percentage
        position_pct = self.calculate_position_percentage(current_price, ath, atl)
        
        analysis = FibonacciAnalysis(
            symbol=symbol,
            ath=ath,
            atl=atl,
            current_price=current_price,
            price_range=ath - atl,
            retracement_levels=retracement_levels,
            extension_levels=extension_levels,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            position_percentage=position_pct
        )
        
        logger.info(
            f"Fibonacci analysis completed for {symbol}: "
            f"position={position_pct}%, support={nearest_support.price if nearest_support else 'N/A'}, "
            f"resistance={nearest_resistance.price if nearest_resistance else 'N/A'}"
        )
        
        return analysis
    
    def calculate_asian_range_fib(
        self, 
        body_high: float, 
        body_low: float
    ) -> float:
        """
        Calculate 50% Fibonacci level for Asian Range.
        
        Args:
            body_high: High of the Asian range body
            body_low: Low of the Asian range body
            
        Returns:
            50% Fibonacci level (midpoint)
            
        Raises:
            ValueError: If body_high <= body_low or values are invalid
        """
        if body_high <= 0 or body_low <= 0:
            raise ValueError("Body high and low must be positive values")
        
        if body_high <= body_low:
            raise ValueError("Body high must be greater than body low")
        
        fib_50 = (body_high + body_low) / 2
        
        logger.debug(
            f"Asian Range 50% Fib: {fib_50} "
            f"(high={body_high}, low={body_low})"
        )
        
        return round(fib_50, 8)
