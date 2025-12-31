"""Coin-related API endpoints."""

import logging
from flask import jsonify, request, current_app
from datetime import datetime

from app.api import api_bp
from app.models import ErrorResponse

logger = logging.getLogger(__name__)


@api_bp.route('/coins', methods=['GET'])
def get_coins():
    """
    Get top coins by market cap.
    
    Query Parameters:
        limit (int): Number of coins to return (default: 100, max: 250)
        include_fibonacci (bool): Include Fibonacci analysis (default: false)
        
    Returns:
        JSON list of coins with market data
    """
    try:
        # Parse query parameters
        limit = min(int(request.args.get('limit', 100)), 250)
        include_fibonacci = request.args.get('include_fibonacci', 'false').lower() == 'true'
        
        # Get filters
        filters = {}
        if 'min_volume' in request.args:
            filters['min_volume'] = request.args.get('min_volume')
        if 'min_market_cap' in request.args:
            filters['min_market_cap'] = request.args.get('min_market_cap')
        if 'min_change_24h' in request.args:
            filters['min_change_24h'] = request.args.get('min_change_24h')
        if 'max_change_24h' in request.args:
            filters['max_change_24h'] = request.args.get('max_change_24h')
        
        logger.info(
            f"GET /coins - limit={limit}, fibonacci={include_fibonacci}, "
            f"filters={filters}"
        )
        
        # Get scanner service from app context
        scanner_service = current_app.scanner_service
        
        # Scan top coins
        result = scanner_service.scan_top_coins(
            limit=limit,
            include_fibonacci=include_fibonacci,
            filters=filters if filters else None
        )
        
        # Convert to dict for JSON serialization
        response = {
            'total_coins': result.total_coins,
            'coins': [coin.model_dump() for coin in result.coins],
            'timestamp': result.timestamp.isoformat(),
            'filters_applied': result.filters_applied
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        logger.warning(f"Invalid parameter: {e}")
        error = ErrorResponse(
            error=f"Invalid parameter: {str(e)}",
            status_code=400
        )
        return jsonify(error.model_dump()), 400
        
    except Exception as e:
        logger.error(f"Error fetching coins: {e}", exc_info=True)
        error = ErrorResponse(
            error="Internal server error",
            status_code=500
        )
        return jsonify(error.model_dump()), 500


@api_bp.route('/coins/<symbol>', methods=['GET'])
def get_coin_by_symbol(symbol: str):
    """
    Get coin data by symbol.
    
    Path Parameters:
        symbol (str): Coin symbol (e.g., 'BTC', 'ETH')
        
    Query Parameters:
        include_fibonacci (bool): Include Fibonacci analysis (default: true)
        
    Returns:
        JSON with coin market data and analysis
    """
    try:
        include_fibonacci = request.args.get('include_fibonacci', 'true').lower() == 'true'
        
        logger.info(f"GET /coins/{symbol} - fibonacci={include_fibonacci}")
        
        # Get scanner service from app context
        scanner_service = current_app.scanner_service
        
        # Get coin data
        coin_data = scanner_service.get_coin_by_symbol(
            symbol=symbol.upper(),
            include_fibonacci=include_fibonacci
        )
        
        if not coin_data:
            error = ErrorResponse(
                error=f"Coin with symbol '{symbol.upper()}' not found",
                status_code=404
            )
            return jsonify(error.model_dump()), 404
        
        return jsonify(coin_data.model_dump()), 200
        
    except Exception as e:
        logger.error(f"Error fetching coin {symbol}: {e}", exc_info=True)
        error = ErrorResponse(
            error="Internal server error",
            status_code=500
        )
        return jsonify(error.model_dump()), 500


@api_bp.route('/coins/<symbol>/fibonacci', methods=['GET'])
def get_fibonacci_analysis(symbol: str):
    """
    Get Fibonacci analysis for a coin.
    
    Path Parameters:
        symbol (str): Coin symbol (e.g., 'BTC', 'ETH')
        
    Returns:
        JSON with Fibonacci retracement and extension levels
    """
    try:
        logger.info(f"GET /coins/{symbol}/fibonacci")
        
        # Get scanner service from app context
        scanner_service = current_app.scanner_service
        
        # Get coin data with Fibonacci analysis
        coin_data = scanner_service.get_coin_by_symbol(
            symbol=symbol.upper(),
            include_fibonacci=True
        )
        
        if not coin_data:
            error = ErrorResponse(
                error=f"Coin with symbol '{symbol.upper()}' not found",
                status_code=404
            )
            return jsonify(error.model_dump()), 404
        
        if not coin_data.fibonacci_analysis:
            error = ErrorResponse(
                error=f"Fibonacci analysis not available for '{symbol.upper()}'",
                status_code=404
            )
            return jsonify(error.model_dump()), 404
        
        return jsonify(coin_data.fibonacci_analysis.model_dump()), 200
        
    except Exception as e:
        logger.error(f"Error fetching Fibonacci for {symbol}: {e}", exc_info=True)
        error = ErrorResponse(
            error="Internal server error",
            status_code=500
        )
        return jsonify(error.model_dump()), 500


@api_bp.route('/coins/<symbol>/ath-atl', methods=['GET'])
def get_ath_atl(symbol: str):
    """
    Get ATH/ATL data for a coin.
    
    Path Parameters:
        symbol (str): Coin symbol (e.g., 'BTC', 'ETH')
        
    Returns:
        JSON with ATH and ATL values
    """
    try:
        logger.info(f"GET /coins/{symbol}/ath-atl")
        
        # Get CoinGecko service from app context
        coingecko_service = current_app.coingecko_service
        
        # First, find the coin ID
        top_coins = coingecko_service.get_top_coins(limit=100)
        coin_id = None
        
        for coin in top_coins:
            if coin.symbol == symbol.upper():
                coin_id = coin.id
                break
        
        if not coin_id:
            error = ErrorResponse(
                error=f"Coin with symbol '{symbol.upper()}' not found",
                status_code=404
            )
            return jsonify(error.model_dump()), 404
        
        # Get ATH/ATL data
        ath_atl_data = coingecko_service.get_coin_ath_atl(coin_id)
        
        if not ath_atl_data:
            error = ErrorResponse(
                error=f"ATH/ATL data not available for '{symbol.upper()}'",
                status_code=404
            )
            return jsonify(error.model_dump()), 404
        
        return jsonify(ath_atl_data.model_dump()), 200
        
    except Exception as e:
        logger.error(f"Error fetching ATH/ATL for {symbol}: {e}", exc_info=True)
        error = ErrorResponse(
            error="Internal server error",
            status_code=500
        )
        return jsonify(error.model_dump()), 500


@api_bp.route('/scan', methods=['POST'])
def scan():
    """
    Scan multiple coins with filters.
    
    Request Body (JSON):
        {
            "limit": 100,
            "include_fibonacci": true,
            "filters": {
                "min_volume": "1000000",
                "min_change_24h": "0"
            }
        }
        
    Returns:
        JSON with scan results
    """
    try:
        data = request.get_json() or {}
        
        limit = min(int(data.get('limit', 100)), 250)
        include_fibonacci = data.get('include_fibonacci', False)
        filters = data.get('filters')
        
        logger.info(
            f"POST /scan - limit={limit}, fibonacci={include_fibonacci}, "
            f"filters={filters}"
        )
        
        # Get scanner service from app context
        scanner_service = current_app.scanner_service
        
        # Perform scan
        result = scanner_service.scan_top_coins(
            limit=limit,
            include_fibonacci=include_fibonacci,
            filters=filters
        )
        
        # Convert to dict for JSON serialization
        response = {
            'total_coins': result.total_coins,
            'coins': [coin.model_dump() for coin in result.coins],
            'timestamp': result.timestamp.isoformat(),
            'filters_applied': result.filters_applied
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error performing scan: {e}", exc_info=True)
        error = ErrorResponse(
            error="Internal server error",
            status_code=500
        )
        return jsonify(error.model_dump()), 500
