# 🚀 Quick Start Guide

Get Trade-Scan up and running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/saracevic/Trade-Scan.git
cd Trade-Scan

# Run setup script (Linux/macOS)
./setup.sh

# Or on Windows
# python -m venv venv
# venv\Scripts\activate
# pip install -r backend/requirements.txt
```

### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/saracevic/Trade-Scan.git
cd Trade-Scan

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Create configuration
cp .env.example .env
```

## Running the Application

### Start Backend API

```bash
# Option 1: Using run script
./run.sh

# Option 2: Manual start
source venv/bin/activate
python backend/main.py
```

The API will be available at: **http://localhost:5000**

### Access Frontend

Simply open `index.html` in your web browser, or serve it with a local server:

```bash
# Python 3
python -m http.server 8080

# Then open http://localhost:8080
```

## Testing the API

### Health Check
```bash
curl http://localhost:5000/api/v1/health
```

### Get Top 10 Coins
```bash
curl "http://localhost:5000/api/v1/coins?limit=10"
```

### Get Bitcoin Data
```bash
curl "http://localhost:5000/api/v1/coins/BTC?include_fibonacci=true"
```

### Get Fibonacci Analysis
```bash
curl "http://localhost:5000/api/v1/coins/ETH/fibonacci"
```

## Docker Deployment

### Quick Start with Docker

```bash
# Build and run
docker build -t trade-scan .
docker run -p 5000:5000 trade-scan
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Backend: http://localhost:5000
# Frontend: http://localhost:8080

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Configuration

Edit `.env` file to customize:

```bash
# Server
PORT=5000
HOST=0.0.0.0

# Cache
CACHE_TTL=300        # 5 minutes
CACHE_MAX_SIZE=1000

# Rate Limiting
COINGECKO_RATE_LIMIT=50  # calls per minute

# Logging
LOG_LEVEL=INFO
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/coins` | GET | Top coins list |
| `/api/v1/coins/{symbol}` | GET | Coin details |
| `/api/v1/coins/{symbol}/fibonacci` | GET | Fibonacci levels |
| `/api/v1/coins/{symbol}/ath-atl` | GET | ATH/ATL data |
| `/api/v1/scan` | POST | Advanced scan |

## Common Issues

### "Module not found" Error
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Port Already in Use
```bash
# Change port in .env file
PORT=5001
```

### CoinGecko Rate Limit
- Free tier: 10-50 calls/minute
- Caching reduces calls by ~80%
- Wait 60 seconds if rate limited

## Next Steps

1. **Read Documentation**: Check `README.md` for detailed information
2. **Explore API**: See `docs/API.md` for all endpoints
3. **Customize**: Edit `.env` for your preferences
4. **Deploy**: Use Docker for production deployment

## Getting Help

- 📚 [README.md](README.md) - Full documentation
- 📖 [API Documentation](docs/API.md) - Endpoint details
- 📝 [Implementation Guide](IMPLEMENTATION.md) - Technical details
- 🐛 [GitHub Issues](https://github.com/saracevic/Trade-Scan/issues) - Report bugs

## Example Usage

### Python Client

```python
import requests

# Get top 5 coins
response = requests.get('http://localhost:5000/api/v1/coins?limit=5')
coins = response.json()['coins']

for coin in coins:
    print(f"{coin['symbol']}: ${coin['current_price']}")
```

### JavaScript/Fetch

```javascript
// Get Bitcoin Fibonacci analysis
fetch('http://localhost:5000/api/v1/coins/BTC/fibonacci')
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL Examples

```bash
# Get top gainers (24h change > 5%)
curl "http://localhost:5000/api/v1/coins?min_change_24h=5"

# Scan with filters
curl -X POST http://localhost:5000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "include_fibonacci": true,
    "filters": {
      "min_volume": "5000000"
    }
  }'
```

## Performance Tips

1. **Enable Caching**: Keep default 5-minute TTL
2. **Limit Requests**: Use filters to reduce data
3. **Use Pagination**: Don't fetch all 100 coins at once
4. **Monitor Rate Limits**: Check `/health` endpoint

## Production Deployment

### Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=WARNING
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

### Using Docker
```bash
docker-compose up -d
```

## Support

Need help? Check:
- Documentation in `docs/` folder
- Example code in `README.md`
- GitHub repository for updates

---

**Ready to analyze crypto markets like a pro!** 🚀📈
