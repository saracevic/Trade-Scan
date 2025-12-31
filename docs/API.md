# API Endpoints Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
No authentication required (public API)

## Rate Limiting
- CoinGecko API: 50 calls/minute (configurable)
- Cache TTL: 5 minutes (reduces repeated calls)

## Endpoints

### 1. Health Check
Check API health status and cache statistics.

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "cache": {
    "hits": 150,
    "misses": 50,
    "hit_rate": 75.0,
    "size": 45,
    "max_size": 1000,
    "ttl": 300
  },
  "version": "1.0.0"
}
```

**Status Codes:**
- 200: Healthy
- 500: Unhealthy

---

### 2. Get Top Coins
Retrieve top cryptocurrencies by market cap with optional Fibonacci analysis.

**Endpoint:** `GET /api/v1/coins`

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 100 | Number of coins (max: 250) |
| include_fibonacci | boolean | No | false | Include Fibonacci analysis |
| min_volume | float | No | - | Minimum 24h volume filter |
| min_market_cap | float | No | - | Minimum market cap filter |
| min_change_24h | float | No | - | Minimum 24h change % |
| max_change_24h | float | No | - | Maximum 24h change % |

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/coins?limit=10&include_fibonacci=true"
```

**Response:**
```json
{
  "total_coins": 10,
  "coins": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "current_price": 43500.0,
      "price_change_24h": 2.5,
      "volume_24h": 25000000000.0,
      "market_cap": 850000000000.0,
      "market_cap_rank": 1,
      "ath": 69000.0,
      "atl": 67.81,
      "fibonacci_analysis": {
        "symbol": "BTC",
        "ath": 69000.0,
        "atl": 67.81,
        "current_price": 43500.0,
        "price_range": 68932.19,
        "position_percentage": 62.95,
        "retracement_levels": [...],
        "extension_levels": [...],
        "nearest_support": {...},
        "nearest_resistance": {...}
      },
      "asian_range": null
    }
  ],
  "timestamp": "2024-01-01T00:00:00.000000",
  "filters_applied": {
    "min_volume": "1000000"
  }
}
```

---

### 3. Get Coin by Symbol
Get detailed data for a specific cryptocurrency.

**Endpoint:** `GET /api/v1/coins/{symbol}`

**Path Parameters:**
- `symbol` (string): Coin symbol (e.g., BTC, ETH, SOL)

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| include_fibonacci | boolean | No | true | Include Fibonacci analysis |

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/coins/BTC?include_fibonacci=true"
```

**Response:** Same as single coin object in `/coins` endpoint

**Status Codes:**
- 200: Success
- 404: Coin not found

---

### 4. Get Fibonacci Analysis
Get Fibonacci retracement and extension levels for a coin.

**Endpoint:** `GET /api/v1/coins/{symbol}/fibonacci`

**Path Parameters:**
- `symbol` (string): Coin symbol

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/coins/BTC/fibonacci"
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
    },
    {
      "level": 0.382,
      "price": 42655.52,
      "label": "38.2%",
      "type": "retracement"
    },
    {
      "level": 0.5,
      "price": 34533.905,
      "label": "50%",
      "type": "retracement"
    },
    {
      "level": 0.618,
      "price": 26412.29,
      "label": "61.8%",
      "type": "retracement"
    },
    {
      "level": 0.786,
      "price": 14823.21,
      "label": "78.6%",
      "type": "retracement"
    },
    {
      "level": 1.0,
      "price": 67.81,
      "label": "100%",
      "type": "retracement"
    }
  ],
  "extension_levels": [
    {
      "level": 1.272,
      "price": 87745.68,
      "label": "127.2%",
      "type": "extension"
    },
    {
      "level": 1.618,
      "price": 111590.15,
      "label": "161.8%",
      "type": "extension"
    },
    {
      "level": 2.618,
      "price": 180468.49,
      "label": "261.8%",
      "type": "extension"
    },
    {
      "level": 4.236,
      "price": 292075.25,
      "label": "423.6%",
      "type": "extension"
    }
  ],
  "nearest_support": {
    "level": 0.382,
    "price": 42655.52,
    "label": "38.2%",
    "type": "retracement"
  },
  "nearest_resistance": {
    "level": 0.236,
    "price": 52732.04,
    "label": "23.6%",
    "type": "retracement"
  }
}
```

---

### 5. Get ATH/ATL Data
Get All-Time High and All-Time Low data for a coin.

**Endpoint:** `GET /api/v1/coins/{symbol}/ath-atl`

**Path Parameters:**
- `symbol` (string): Coin symbol

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/coins/ETH/ath-atl"
```

**Response:**
```json
{
  "ath": 4878.26,
  "ath_date": "2021-11-10T14:24:11.849000+00:00",
  "atl": 0.432979,
  "atl_date": "2015-10-20T00:00:00+00:00",
  "current_price": 2245.67
}
```

---

### 6. Scan Multiple Coins
Scan multiple coins with custom filters (POST request for complex queries).

**Endpoint:** `POST /api/v1/scan`

**Request Body:**
```json
{
  "limit": 100,
  "include_fibonacci": true,
  "filters": {
    "min_volume": "1000000",
    "min_change_24h": "0",
    "min_fib_position": "30",
    "max_fib_position": "70"
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "include_fibonacci": true,
    "filters": {
      "min_volume": "5000000",
      "min_change_24h": "2"
    }
  }'
```

**Response:** Same as `/coins` endpoint

---

## Fibonacci Levels Explained

### Retracement Levels (0% - 100%)
These levels indicate potential support zones when price retraces from ATH:
- **0% (ATH)**: All-time high price
- **23.6%**: First retracement level
- **38.2%**: Shallow retracement
- **50%**: Midpoint (strongest support/resistance)
- **61.8%**: Golden ratio
- **78.6%**: Deep retracement
- **100% (ATL)**: All-time low price

### Extension Levels (>100%)
These levels indicate potential resistance zones beyond ATH:
- **127.2%**: First extension
- **161.8%**: Golden extension
- **261.8%**: Major extension
- **423.6%**: Extreme extension

### Position Percentage
Indicates where the current price is positioned between ATL (0%) and ATH (100%):
- **0-25%**: Near all-time low (potential buy zone)
- **25-50%**: Below midpoint
- **50-75%**: Above midpoint
- **75-100%**: Near all-time high (potential overbought)

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

**Common Status Codes:**
- 400: Bad Request (invalid parameters)
- 404: Not Found (coin doesn't exist)
- 429: Too Many Requests (rate limited)
- 500: Internal Server Error

---

## Examples

### Get Top 10 Gainers
```bash
curl "http://localhost:5000/api/v1/coins?limit=100&min_change_24h=5"
```

### Get Coins in "Buy Zone" (Position < 30%)
```bash
curl -X POST http://localhost:5000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 100,
    "include_fibonacci": true,
    "filters": {
      "max_fib_position": "30"
    }
  }'
```

### Get High Volume Coins with Positive Change
```bash
curl "http://localhost:5000/api/v1/coins?limit=50&min_volume=10000000&min_change_24h=0"
```

---

## Notes

1. **Caching**: Results are cached for 5 minutes to reduce API calls
2. **Rate Limiting**: Respects CoinGecko's rate limits (50 calls/minute)
3. **Concurrent Processing**: Uses thread pools for parallel coin scanning
4. **Type Safety**: All responses validated with Pydantic models
5. **Error Handling**: Automatic retries with exponential backoff

---

## Rate Limits

**CoinGecko API (Free Tier):**
- 10-50 calls per minute
- Rate limiting handled automatically
- Caching reduces actual API calls by ~80%

**Binance Futures API:**
- 1200 weight per minute
- Used for Asian Range calculations
- No authentication required
