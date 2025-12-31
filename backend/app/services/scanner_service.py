"""
Scanner service for Trade-Scan application.

This module provides the main scanning functionality that combines
CoinGecko data, Fibonacci analysis, and Asian Range calculations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models import CoinMarketData, ScanResult, FibonacciAnalysis
from app.services.coingecko_service import CoinGeckoService
from app.services.fibonacci_service import FibonacciService
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class ScannerService:
    """
    Main scanner service for multi-coin analysis.
    
    This service coordinates between CoinGecko, Fibonacci, and Asian Range
    services to provide comprehensive cryptocurrency analysis.
    """
    
    def __init__(
        self,
        coingecko_service: CoinGeckoService,
        fibonacci_service: FibonacciService,
        cache_service: Optional[CacheService] = None
    ):
        """
        Initialize scanner service.
        
        Args:
            coingecko_service: CoinGecko service instance
            fibonacci_service: Fibonacci service instance
            cache_service: Cache service instance (optional)
        """
        self.coingecko_service = coingecko_service
        self.fibonacci_service = fibonacci_service
        self.cache_service = cache_service
        logger.info("ScannerService initialized")
    
    def scan_coin(
        self,
        coin_id: str,
        include_fibonacci: bool = True
    ) -> Optional[CoinMarketData]:
        """
        Scan a single coin with complete analysis.
        
        Args:
            coin_id: CoinGecko coin ID
            include_fibonacci: Whether to include Fibonacci analysis
            
        Returns:
            CoinMarketData with analysis or None if failed
        """
        try:
            # Get basic market data
            market_data = self.coingecko_service.get_coin_market_data(coin_id)
            if not market_data:
                logger.warning(f"Failed to get market data for {coin_id}")
                return None
            
            # Add Fibonacci analysis if requested
            if include_fibonacci and market_data.ath and market_data.atl:
                try:
                    # Get detailed ATH/ATL data
                    ath_atl_data = self.coingecko_service.get_coin_ath_atl(coin_id)
                    if ath_atl_data:
                        fibonacci_analysis = self.fibonacci_service.analyze(
                            symbol=market_data.symbol,
                            ath_atl_data=ath_atl_data
                        )
                        market_data.fibonacci_analysis = fibonacci_analysis
                except Exception as e:
                    logger.warning(
                        f"Failed to calculate Fibonacci for {coin_id}: {e}"
                    )
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error scanning coin {coin_id}: {e}")
            return None
    
    def scan_multiple_coins(
        self,
        coin_ids: List[str],
        include_fibonacci: bool = True,
        max_workers: int = 10
    ) -> List[CoinMarketData]:
        """
        Scan multiple coins concurrently.
        
        Args:
            coin_ids: List of CoinGecko coin IDs
            include_fibonacci: Whether to include Fibonacci analysis
            max_workers: Maximum concurrent workers
            
        Returns:
            List of CoinMarketData objects (successful scans only)
        """
        results = []
        total = len(coin_ids)
        completed = 0
        
        logger.info(
            f"Starting scan of {total} coins "
            f"(fibonacci={include_fibonacci}, workers={max_workers})"
        )
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_coin = {
                executor.submit(
                    self.scan_coin, 
                    coin_id, 
                    include_fibonacci
                ): coin_id
                for coin_id in coin_ids
            }
            
            # Process completed tasks
            for future in as_completed(future_to_coin):
                coin_id = future_to_coin[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.debug(
                            f"[{completed}/{total}] Successfully scanned {coin_id}"
                        )
                    else:
                        logger.warning(
                            f"[{completed}/{total}] Failed to scan {coin_id}"
                        )
                except Exception as e:
                    logger.error(
                        f"[{completed}/{total}] Exception scanning {coin_id}: {e}"
                    )
        
        logger.info(
            f"Scan completed: {len(results)}/{total} coins successful"
        )
        return results
    
    def scan_top_coins(
        self,
        limit: int = 100,
        include_fibonacci: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> ScanResult:
        """
        Scan top coins by market cap.
        
        Args:
            limit: Number of top coins to scan
            include_fibonacci: Whether to include Fibonacci analysis
            filters: Optional filters to apply
            
        Returns:
            ScanResult with analyzed coins
        """
        logger.info(f"Scanning top {limit} coins...")
        
        # Get top coins list
        top_coins = self.coingecko_service.get_top_coins(limit=limit)
        if not top_coins:
            logger.error("Failed to fetch top coins list")
            return ScanResult(
                total_coins=0,
                coins=[],
                timestamp=datetime.utcnow(),
                filters_applied=filters
            )
        
        # Extract coin IDs
        coin_ids = [coin.id for coin in top_coins]
        
        # Scan all coins
        scanned_coins = self.scan_multiple_coins(
            coin_ids=coin_ids,
            include_fibonacci=include_fibonacci,
            max_workers=10
        )
        
        # Apply filters if provided
        if filters:
            scanned_coins = self._apply_filters(scanned_coins, filters)
        
        # Sort by market cap rank
        scanned_coins.sort(
            key=lambda x: x.market_cap_rank if x.market_cap_rank else 9999
        )
        
        result = ScanResult(
            total_coins=len(scanned_coins),
            coins=scanned_coins,
            timestamp=datetime.utcnow(),
            filters_applied=filters
        )
        
        logger.info(
            f"Scan completed: {result.total_coins} coins "
            f"(filters: {filters is not None})"
        )
        
        return result
    
    def _apply_filters(
        self,
        coins: List[CoinMarketData],
        filters: Dict[str, Any]
    ) -> List[CoinMarketData]:
        """
        Apply filters to coin list.
        
        Args:
            coins: List of coins to filter
            filters: Filter criteria
            
        Returns:
            Filtered coin list
        """
        filtered = coins
        
        # Filter by minimum volume
        if "min_volume" in filters:
            min_vol = float(filters["min_volume"])
            filtered = [
                c for c in filtered 
                if c.volume_24h and c.volume_24h >= min_vol
            ]
        
        # Filter by minimum market cap
        if "min_market_cap" in filters:
            min_cap = float(filters["min_market_cap"])
            filtered = [
                c for c in filtered 
                if c.market_cap and c.market_cap >= min_cap
            ]
        
        # Filter by price change
        if "min_change_24h" in filters:
            min_change = float(filters["min_change_24h"])
            filtered = [c for c in filtered if c.price_change_24h >= min_change]
        
        if "max_change_24h" in filters:
            max_change = float(filters["max_change_24h"])
            filtered = [c for c in filtered if c.price_change_24h <= max_change]
        
        # Filter by Fibonacci position
        if "min_fib_position" in filters:
            min_pos = float(filters["min_fib_position"])
            filtered = [
                c for c in filtered 
                if c.fibonacci_analysis and 
                c.fibonacci_analysis.position_percentage >= min_pos
            ]
        
        if "max_fib_position" in filters:
            max_pos = float(filters["max_fib_position"])
            filtered = [
                c for c in filtered 
                if c.fibonacci_analysis and 
                c.fibonacci_analysis.position_percentage <= max_pos
            ]
        
        logger.info(
            f"Filters applied: {len(coins)} -> {len(filtered)} coins"
        )
        
        return filtered
    
    def get_coin_by_symbol(
        self,
        symbol: str,
        include_fibonacci: bool = True
    ) -> Optional[CoinMarketData]:
        """
        Get coin data by symbol.
        
        Args:
            symbol: Coin symbol (e.g., 'BTC', 'ETH')
            include_fibonacci: Whether to include Fibonacci analysis
            
        Returns:
            CoinMarketData or None if not found
        """
        symbol = symbol.upper()
        
        # Search in top coins to find the coin ID
        top_coins = self.coingecko_service.get_top_coins(limit=100)
        
        coin_id = None
        for coin in top_coins:
            if coin.symbol == symbol:
                coin_id = coin.id
                break
        
        if not coin_id:
            logger.warning(f"Coin with symbol {symbol} not found in top 100")
            return None
        
        return self.scan_coin(coin_id, include_fibonacci)
