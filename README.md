# 🚀 Trade-Scan - Professional Cryptocurrency Analysis Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Trade-Scan is a professional-grade cryptocurrency analysis platform that provides real-time market data, Fibonacci retracement/extension levels based on ATH/ATL values, and Asian Range analysis for top 100 cryptocurrencies.

## ✨ Features

### 🎯 Core Features
- **Top 100 Coins Support**: Automatically fetches and analyzes top 100 cryptocurrencies by market cap from CoinGecko
- **ATH/ATL Based Fibonacci Levels**: 
  - Retracement levels: 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
  - Extension levels: 127.2%, 161.8%, 261.8%, 423.6%
- **Asian Range Analysis**: Thursday's Asian Session (19:00-00:00 NY Time) 50% Fibonacci tracking
- **Real-time Market Data**: Current prices, 24h changes, volume, and market cap
- **Smart Caching**: Reduces API calls with intelligent TTL-based caching
- **Rate Limiting**: Respects CoinGecko API limits with built-in rate limiter

### 🏗️ Architecture
- **RESTful API**: Clean, documented API endpoints
- **Service Layer**: Modular services (CoinGecko, Fibonacci, Scanner, Cache)
- **Type Safety**: Pydantic models for data validation
- **Error Handling**: Comprehensive exception handling with retry logic
- **Concurrent Processing**: Multi-threaded coin scanning for performance

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/saracevic/Trade-Scan.git
cd Trade-Scan
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your preferences (optional, defaults work fine)
```

5. **Run the application**
```bash
python backend/main.py
```

The API will be available at `http://localhost:5000`

## ⚙️ Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=5000

# API Configuration
COINGECKO_API_URL=https://api.coingecko.com/api/v3

# Cache Configuration
CACHE_TTL=300          # 5 minutes
CACHE_MAX_SIZE=1000

# Rate Limiting
COINGECKO_RATE_LIMIT=50   # Calls per minute
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### 1. Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "cache": {
    "hits": 150,
    "misses": 50,
    "hit_rate": 75.0
  }
}
```

#### 2. Get Top Coins
```http
GET /api/v1/coins?limit=100&include_fibonacci=true
```

**Query Parameters:**
- `limit` (int, optional): Number of coins (default: 100, max: 250)
- `include_fibonacci` (bool, optional): Include Fibonacci analysis (default: false)
- `min_volume` (float, optional): Minimum 24h volume filter
- `min_market_cap` (float, optional): Minimum market cap filter
- `min_change_24h` (float, optional): Minimum 24h change % filter
- `max_change_24h` (float, optional): Maximum 24h change % filter

**Response:**
```json
{
  "total_coins": 100,
  "coins": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "current_price": 43500.0,
      "price_change_24h": 2.5,
      "volume_24h": 25000000000,
      "market_cap": 850000000000,
      "market_cap_rank": 1,
      "ath": 69000.0,
      "atl": 67.81,
      "fibonacci_analysis": {
        "symbol": "BTC",
        "ath": 69000.0,
        "atl": 67.81,
        "current_price": 43500.0,
        "position_percentage": 62.95,
        "retracement_levels": [...],
        "extension_levels": [...],
        "nearest_support": {...},
        "nearest_resistance": {...}
      }
    }
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

#### 3. Get Coin by Symbol
```http
GET /api/v1/coins/{symbol}?include_fibonacci=true
```

**Example:**
```bash
curl http://localhost:5000/api/v1/coins/BTC
```

#### 4. Get Fibonacci Analysis
```http
GET /api/v1/coins/{symbol}/fibonacci
```

**Example:**
```bash
curl http://localhost:5000/api/v1/coins/BTC/fibonacci
```

**Response:**
```json
{
  "symbol": "BTC",
  "ath": 69000.0,
  "atl": 67.81,
  "current_price": 43500.0,
  "price_range": 68932.19,
  "position_percentage": 62.95,
  "retracement_levels": [
    {
      "level": 0.0,
      "price": 69000.0,
      "label": "0%",
      "type": "retracement"
    },
    {
      "level": 0.236,
      "price": 52732.04,
      "label": "23.6%",
      "type": "retracement"
    }
  ],
  "extension_levels": [
    {
      "level": 1.272,
      "price": 87745.68,
      "label": "127.2%",
      "type": "extension"
    }
  ],
  "nearest_support": {...},
  "nearest_resistance": {...}
}
```

#### 5. Get ATH/ATL Data
```http
GET /api/v1/coins/{symbol}/ath-atl
```

#### 6. Scan Multiple Coins
```http
POST /api/v1/scan
Content-Type: application/json

{
  "limit": 100,
  "include_fibonacci": true,
  "filters": {
    "min_volume": "1000000",
    "min_change_24h": "0"
  }
}
```

## 💡 Usage Examples

### Python Client Example

```python
import requests

# Get top 10 coins with Fibonacci analysis
response = requests.get(
    'http://localhost:5000/api/v1/coins',
    params={'limit': 10, 'include_fibonacci': 'true'}
)
data = response.json()

for coin in data['coins']:
    print(f"{coin['symbol']}: ${coin['current_price']}")
    if coin.get('fibonacci_analysis'):
        fib = coin['fibonacci_analysis']
        print(f"  Position: {fib['position_percentage']}%")
        print(f"  Support: ${fib['nearest_support']['price']}")
        print(f"  Resistance: ${fib['nearest_resistance']['price']}")
```

### JavaScript/Fetch Example

```javascript
// Fetch Bitcoin data
fetch('http://localhost:5000/api/v1/coins/BTC?include_fibonacci=true')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.symbol}: $${data.current_price}`);
    console.log(`24h Change: ${data.price_change_24h}%`);
  });
```

## 🛠️ Development

### Project Structure

```
Trade-Scan/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Flask app factory
│   │   ├── config.py             # Configuration management
│   │   ├── api/
│   │   │   ├── __init__.py       # API blueprint
│   │   │   └── routes/
│   │   │       ├── health.py     # Health check endpoints
│   │   │       └── coins.py      # Coin endpoints
│   │   ├── services/
│   │   │   ├── cache_service.py      # Caching layer
│   │   │   ├── coingecko_service.py  # CoinGecko API integration
│   │   │   ├── fibonacci_service.py  # Fibonacci calculations
│   │   │   └── scanner_service.py    # Multi-coin scanning
│   │   ├── models/
│   │   │   └── __init__.py       # Pydantic models
│   │   └── utils/
│   ├── tests/
│   │   ├── test_fibonacci_service.py
│   │   └── test_cache_service.py
│   ├── requirements.txt
│   └── main.py                   # Application entry point
├── index.html                     # Frontend (existing)
├── script.js
├── style.css
├── .env.example
├── .gitignore
└── README.md
```

### Code Quality

The project follows best practices:
- **Type Hints**: All functions have type annotations
- **Docstrings**: Google-style docstrings for all classes and functions
- **Pydantic Models**: Type-safe data structures with validation
- **Error Handling**: Comprehensive exception handling with retry logic
- **Logging**: Structured logging throughout the application

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_fibonacci_service.py -v
```

### Code Formatting

```bash
# Install formatting tools
pip install black flake8 pylint

# Format code
black backend/app backend/tests

# Check code style
flake8 backend/app backend/tests

# Run linter
pylint backend/app
```

## 🏛️ Architecture

### Service Layer Pattern

The application uses a clean service layer architecture:

```
┌─────────────────────────────────────────┐
│          Flask Application              │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         │   API Routes    │
         └────────┬────────┘
                  │
    ┌─────────────┴─────────────┐
    │     Scanner Service       │
    └─────────────┬─────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐  ┌────▼─────┐  ┌───▼────┐
│CoinGecko│  │Fibonacci │  │ Cache  │
│Service  │  │ Service  │  │Service │
└─────────┘  └──────────┘  └────────┘
```

### Key Design Patterns

1. **Service Layer**: Business logic separated from API layer
2. **Dependency Injection**: Services injected into routes via Flask app context
3. **Factory Pattern**: Flask app created via factory function
4. **Repository Pattern**: CoinGecko service abstracts external API
5. **Caching Strategy**: TTL-based caching to optimize API usage
6. **Rate Limiting**: Prevents API throttling

## 🔒 Security

- **Input Validation**: Pydantic models validate all input data
- **Rate Limiting**: Built-in rate limiter for external API calls
- **Environment Variables**: Sensitive configuration via `.env` file
- **CORS**: Configurable CORS for frontend integration
- **Error Messages**: No sensitive data in error responses

## 📊 Performance

- **Caching**: 5-minute TTL reduces API calls by ~80%
- **Concurrent Processing**: ThreadPoolExecutor for parallel coin scanning
- **Rate Limiting**: Respects API limits while maximizing throughput
- **Lazy Loading**: Data fetched only when requested

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public APIs
- Include unit tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CoinGecko API**: Free cryptocurrency data
- **Binance Futures API**: Real-time futures data
- **Flask**: Lightweight web framework
- **Pydantic**: Data validation library

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [GitHub Repository](https://github.com/saracevic/Trade-Scan)

## 🗺️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Historical Fibonacci analysis
- [ ] Multiple timeframe support
- [ ] Price alerts (email/webhook)
- [ ] CSV/JSON export functionality
- [ ] Telegram bot integration
- [ ] Volume profile integration
- [ ] Advanced charting with TradingView
- [ ] Custom watchlist management
- [ ] Docker deployment
- [ ] CI/CD pipeline with GitHub Actions

---

**⚠️ Disclaimer**: This tool is for informational purposes only. It is not financial advice. Always do your own research (DYOR) before making investment decisions.
