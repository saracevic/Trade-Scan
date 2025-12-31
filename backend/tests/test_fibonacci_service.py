"""Unit tests for Fibonacci service."""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.fibonacci_service import FibonacciService
from app.models import ATHATLData


@pytest.fixture
def fibonacci_service():
    """Create a Fibonacci service instance."""
    return FibonacciService()


class TestFibonacciService:
    """Test cases for FibonacciService."""
    
    def test_calculate_retracement_levels(self, fibonacci_service):
        """Test Fibonacci retracement level calculation."""
        ath = 69000.0
        atl = 67.81
        
        levels = fibonacci_service.calculate_retracement_levels(ath, atl)
        
        assert len(levels) == 7
        assert levels[0].level == 0.0
        assert levels[0].price == ath
        assert levels[-1].level == 1.0
        assert levels[-1].price == atl
        
        # Check 50% level
        fib_50 = next(l for l in levels if l.level == 0.5)
        expected_50 = ath - ((ath - atl) * 0.5)
        assert abs(fib_50.price - expected_50) < 0.01
    
    def test_calculate_extension_levels(self, fibonacci_service):
        """Test Fibonacci extension level calculation."""
        ath = 69000.0
        atl = 67.81
        
        levels = fibonacci_service.calculate_extension_levels(ath, atl)
        
        assert len(levels) == 4
        assert all(l.price > ath for l in levels)
        assert levels[0].level == 1.272
        assert levels[-1].level == 4.236
    
    def test_calculate_position_percentage(self, fibonacci_service):
        """Test position percentage calculation."""
        ath = 100.0
        atl = 0.0
        
        # At ATL (0%)
        pos = fibonacci_service.calculate_position_percentage(0.0, ath, atl)
        assert pos == 0.0
        
        # At ATH (100%)
        pos = fibonacci_service.calculate_position_percentage(100.0, ath, atl)
        assert pos == 100.0
        
        # At midpoint (50%)
        pos = fibonacci_service.calculate_position_percentage(50.0, ath, atl)
        assert pos == 50.0
    
    def test_analyze(self, fibonacci_service):
        """Test complete Fibonacci analysis."""
        ath_atl_data = ATHATLData(
            ath=69000.0,
            atl=67.81,
            current_price=43500.0
        )
        
        analysis = fibonacci_service.analyze("BTC", ath_atl_data)
        
        assert analysis.symbol == "BTC"
        assert analysis.ath == 69000.0
        assert analysis.atl == 67.81
        assert analysis.current_price == 43500.0
        assert len(analysis.retracement_levels) == 7
        assert len(analysis.extension_levels) == 4
        assert 0 <= analysis.position_percentage <= 100
    
    def test_invalid_ath_atl(self, fibonacci_service):
        """Test error handling for invalid ATH/ATL."""
        with pytest.raises(ValueError):
            fibonacci_service.calculate_retracement_levels(100.0, 200.0)
        
        with pytest.raises(ValueError):
            fibonacci_service.calculate_retracement_levels(-100.0, 50.0)
    
    def test_asian_range_fib(self, fibonacci_service):
        """Test Asian Range 50% Fibonacci calculation."""
        body_high = 44000.0
        body_low = 43000.0
        
        fib_50 = fibonacci_service.calculate_asian_range_fib(body_high, body_low)
        
        expected = (body_high + body_low) / 2
        assert abs(fib_50 - expected) < 0.01
    
    def test_asian_range_invalid(self, fibonacci_service):
        """Test Asian Range with invalid values."""
        with pytest.raises(ValueError):
            fibonacci_service.calculate_asian_range_fib(43000.0, 44000.0)
