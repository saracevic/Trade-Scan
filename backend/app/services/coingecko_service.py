"""
CoinGecko API service for Trade-Scan application.

This module provides integration with CoinGecko API to fetch cryptocurrency
market data, including top coins, ATH/ATL values, and current prices.
"""

import time
import requests
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.config import config
from app.models import CoinInfo, ATHATLData, CoinMarketData
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 50):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum API calls per minute
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time = 0.0
    
    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()


class CoinGeckoService:
    """
    Service for interacting with CoinGecko API.
    
    This service provides methods to fetch cryptocurrency data from CoinGecko,
    including market data, ATH/ATL values, and top coins by market cap.
    Features rate limiting and caching to optimize API usage.
    """
    
    def __init__(self, cache_service: Optional[CacheService] = None):
        """
        Initialize CoinGecko service.
        
        Args:
            cache_service: Cache service instance (optional)
        """
        self.base_url = config.COINGECKO_API_URL
        self.cache_service = cache_service
        self.rate_limiter = RateLimiter(
            calls_per_minute=config.COINGECKO_RATE_LIMIT
        )
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Trade-Scan/1.0"
        })
        logger.info("CoinGeckoService initialized")
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to CoinGecko API with retry logic.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            retry_count: Number of retry attempts
            
        Returns:
            JSON response or None if failed
        """
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(retry_count):
            try:
                self.rate_limiter.wait_if_needed()
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    # Check for Retry-After header
                    retry_after = response.headers.get('Retry-After', '60')
                    try:
                        wait_time = int(retry_after)
                    except ValueError:
                        wait_time = 60
                    
                    logger.warning(
                        f"Rate limited by CoinGecko. "
                        f"Waiting {wait_time}s (attempt {attempt + 1}/{retry_count})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"CoinGecko API error: {response.status_code} - {response.text}"
                    )
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Request failed (attempt {attempt + 1}/{retry_count}): {e}"
                )
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def get_top_coins(
        self, 
        limit: int = 100,
        use_cache: bool = True
    ) -> List[CoinInfo]:
        """
        Get top coins by market capitalization.
        
        Args:
            limit: Number of top coins to fetch (default: 100)
            use_cache: Whether to use cached data (default: True)
            
        Returns:
            List of CoinInfo objects
        """
        cache_key = f"top_coins:{limit}"
        
        # Try cache first
        if use_cache and self.cache_service:
            cached = self.cache_service.get(cache_key)
            if cached:
                logger.info(f"Retrieved {len(cached)} top coins from cache")
                return cached
        
        # Fetch from API
        logger.info(f"Fetching top {limit} coins from CoinGecko...")
        
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": min(limit, 250),
            "page": 1,
            "sparkline": False
        }
        
        data = self._make_request("coins/markets", params)
        
        if not data:
            logger.error("Failed to fetch top coins from CoinGecko")
            return []
        
        coins = []
        for item in data[:limit]:
            try:
                coin = CoinInfo(
                    id=item["id"],
                    symbol=item["symbol"].upper(),
                    name=item["name"],
                    market_cap_rank=item.get("market_cap_rank")
                )
                coins.append(coin)
            except Exception as e:
                logger.warning(f"Failed to parse coin data: {e}")
                continue
        
        # Cache the result
        if self.cache_service:
            self.cache_service.set(cache_key, coins)
        
        logger.info(f"Successfully fetched {len(coins)} top coins")
        return coins
    
    def get_coin_ath_atl(
        self, 
        coin_id: str,
        use_cache: bool = True
    ) -> Optional[ATHATLData]:
        """
        Get ATH/ATL data for a specific coin.
        
        Args:
            coin_id: CoinGecko coin ID
            use_cache: Whether to use cached data (default: True)
            
        Returns:
            ATHATLData object or None if failed
        """
        cache_key = f"ath_atl:{coin_id}"
        
        # Try cache first
        if use_cache and self.cache_service:
            cached = self.cache_service.get(cache_key)
            if cached:
                logger.debug(f"Retrieved ATH/ATL for {coin_id} from cache")
                return cached
        
        # Fetch from API
        logger.debug(f"Fetching ATH/ATL data for {coin_id}...")
        
        params = {
            "localization": False,
            "tickers": False,
            "market_data": True,
            "community_data": False,
            "developer_data": False
        }
        
        data = self._make_request(f"coins/{coin_id}", params)
        
        if not data or "market_data" not in data:
            logger.error(f"Failed to fetch ATH/ATL data for {coin_id}")
            return None
        
        try:
            market_data = data["market_data"]
            
            ath_atl = ATHATLData(
                ath=market_data["ath"]["usd"],
                ath_date=datetime.fromisoformat(
                    market_data["ath_date"]["usd"].replace("Z", "+00:00")
                ) if market_data.get("ath_date", {}).get("usd") else None,
                atl=market_data["atl"]["usd"],
                atl_date=datetime.fromisoformat(
                    market_data["atl_date"]["usd"].replace("Z", "+00:00")
                ) if market_data.get("atl_date", {}).get("usd") else None,
                current_price=market_data["current_price"]["usd"]
            )
            
            # Cache the result
            if self.cache_service:
                self.cache_service.set(cache_key, ath_atl)
            
            logger.debug(
                f"ATH/ATL for {coin_id}: ATH=${ath_atl.ath}, ATL=${ath_atl.atl}"
            )
            return ath_atl
            
        except Exception as e:
            logger.error(f"Failed to parse ATH/ATL data for {coin_id}: {e}")
            return None
    
    def get_coin_market_data(
        self, 
        coin_id: str,
        use_cache: bool = True
    ) -> Optional[CoinMarketData]:
        """
        Get complete market data for a coin.
        
        Args:
            coin_id: CoinGecko coin ID
            use_cache: Whether to use cached data (default: True)
            
        Returns:
            CoinMarketData object or None if failed
        """
        cache_key = f"market_data:{coin_id}"
        
        # Try cache first
        if use_cache and self.cache_service:
            cached = self.cache_service.get(cache_key)
            if cached:
                logger.debug(f"Retrieved market data for {coin_id} from cache")
                return cached
        
        # Fetch from API
        params = {
            "ids": coin_id,
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "sparkline": False
        }
        
        data = self._make_request("coins/markets", params)
        
        if not data or len(data) == 0:
            logger.error(f"Failed to fetch market data for {coin_id}")
            return None
        
        try:
            item = data[0]
            market_data = CoinMarketData(
                symbol=item["symbol"].upper(),
                name=item["name"],
                current_price=item["current_price"],
                price_change_24h=item.get("price_change_percentage_24h", 0),
                volume_24h=item.get("total_volume"),
                market_cap=item.get("market_cap"),
                market_cap_rank=item.get("market_cap_rank"),
                ath=item.get("ath"),
                atl=item.get("atl")
            )
            
            # Cache the result (shorter TTL for market data)
            if self.cache_service:
                self.cache_service.set(cache_key, market_data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to parse market data for {coin_id}: {e}")
            return None
