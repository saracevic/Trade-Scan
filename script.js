let coinsData = [];
let filteredCoins = [];
let currentFilter = 'all';
let sortDirection = {
    symbol: 1,
    price: 1,
    change: 1,
    high: 1,
    low:  1,
    ath: 1,
    atl: 1
};

// Sayfa yüklendiğinde
window.addEventListener('load', () => {
    console.log('Page loaded, starting data fetch...');
    loadData();
    updateMarketStatus();
});

// Market durumunu güncelle
function updateMarketStatus() {
    const statusElement = document.getElementById('marketStatus');
    if (statusElement) {
        statusElement.textContent = 'LIVE';
        statusElement.style. color = 'var(--color-positive)';
    }
}

// Verileri API'lerden çek
async function loadData() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const table = document.querySelector('.table-wrapper');
    
    console.log('Loading data...');
    
    if (loading) loading.style.display = 'block';
    if (error) error.style.display = 'none';
    if (table) table.style.display = 'none';

    try {
        // Timeout ekle (10 saniye)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        console.log('Fetching Binance data...');
        
        // Binance Futures API
        const binanceResponse = await fetch('https://fapi.binance.com/fapi/v1/ticker/24hr', {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);

        if (!binanceResponse.ok) {
            throw new Error(`Binance API error: ${binanceResponse.status}`);
        }

        const binanceData = await binanceResponse.json();
        console.log('Binance data received:', binanceData. length, 'items');
        
        // USDT perpetual futures filtrele
        const futuresCoins = binanceData
            .filter(coin => coin. symbol.endsWith('USDT'))
            .map(coin => ({
                symbol:  coin.symbol.replace('USDT', ''),
                price: parseFloat(coin.lastPrice),
                change: parseFloat(coin.priceChangePercent),
                high: parseFloat(coin.highPrice),
                low: parseFloat(coin.lowPrice),
                volume: parseFloat(coin.volume),
                ath: null,
                atl: null
            }));

        console.log('Filtered coins:', futuresCoins.length);

        // CoinGecko API (ATH/ATL için) - Hata olsa bile devam et
        const coinGeckoMap = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
            'XRP': 'ripple', 'ADA': 'cardano', 'DOGE': 'dogecoin',
            'SOL': 'solana', 'TRX': 'tron', 'DOT': 'polkadot',
            'MATIC': 'matic-network', 'LTC': 'litecoin', 'SHIB': 'shiba-inu',
            'AVAX': 'avalanche-2', 'UNI': 'uniswap', 'LINK': 'chainlink',
            'ATOM': 'cosmos', 'XLM': 'stellar', 'ETC': 'ethereum-classic',
            'BCH': 'bitcoin-cash', 'NEAR': 'near', 'APT': 'aptos',
            'FIL': 'filecoin', 'ARB': 'arbitrum', 'OP': 'optimism',
            'INJ': 'injective-protocol', 'SUI': 'sui', 'PEPE': 'pepe'
        };

        const coinGeckoIds = Object.values(coinGeckoMap).join(',');
        
        try {
            console.log('Fetching CoinGecko data...');
            const geckoController = new AbortController();
            const geckoTimeoutId = setTimeout(() => geckoController.abort(), 5000);

            const geckoResponse = await fetch(
                `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${coinGeckoIds}&order=market_cap_desc&sparkline=false`,
                { signal: geckoController.signal }
            );
            
            clearTimeout(geckoTimeoutId);

            if (geckoResponse.ok) {
                const geckoData = await geckoResponse.json();
                console.log('CoinGecko data received:', geckoData.length, 'items');
                
                geckoData.forEach(geckoCoin => {
                    const symbol = Object.keys(coinGeckoMap).find(
                        key => coinGeckoMap[key] === geckoCoin.id
                    );
                    
                    if (symbol) {
                        const coin = futuresCoins.find(c => c.symbol === symbol);
                        if (coin) {
                            coin.ath = geckoCoin.ath;
                            coin.atl = geckoCoin.atl;
                        }
                    }
                });
            }
        } catch (geckoError) {
            console. warn('CoinGecko data unavailable (continuing without ATH/ATL):', geckoError. message);
        }

        coinsData = futuresCoins;
        filteredCoins = [... coinsData];

        // Varsayılan sıralama:  değişime göre
        coinsData.sort((a, b) => b.change - a.change);
        filteredCoins.sort((a, b) => b.change - a.change);

        console.log('Displaying coins.. .');
        displayCoins(filteredCoins);
        updateStats(coinsData);
        updateLastUpdateTime();

        if (loading) loading.style.display = 'none';
        if (table) table.style.display = 'block';
        
        console.log('Data loaded successfully! ');

    } catch (err) {
        console.error('Error loading data:', err);
        
        if (loading) loading.style.display = 'none';
        if (error) {
            error.style.display = 'block';
            // Hata mesajını güncelle
            const errorText = error.querySelector('p');
            if (errorText) {
                if (err.name === 'AbortError') {
                    errorText. textContent = '⏱️ Request timeout.  Please check your connection and try again.';
                } else {
                    errorText. textContent = `❌ ${err.message}.  Please try again.`;
                }
            }
        }
    }
}

// Coinleri tabloda göster
function displayCoins(coins) {
    const tbody = document.getElementById('coinsBody');
    if (!tbody) {
        console.error('Table body not found! ');
        return;
    }
    
    tbody.innerHTML = '';

    if (coins.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--text-secondary);">No coins found</td></tr>';
        return;
    }

    coins.forEach(coin => {
        const row = document.createElement('tr');
        
        const changeClass = coin.change > 0 ? 'positive-change' :  
                           coin.change < 0 ? 'negative-change' : 'neutral-change';
        const changeSymbol = coin.change > 0 ? '+' : '';

        const athDisplay = coin.ath ? `$${formatNumber(coin.ath)}` : '-';
        const atlDisplay = coin.atl ? `$${formatNumber(coin.atl)}` : '-';

        row.innerHTML = `
            <td><div class="coin-symbol">${coin.symbol}</div></td>
            <td class="text-right price">$${formatNumber(coin.price)}</td>
            <td class="text-right"><span class="change ${changeClass}">${changeSymbol}${coin.change. toFixed(2)}%</span></td>
            <td class="text-right">$${formatNumber(coin.high)}</td>
            <td class="text-right">$${formatNumber(coin.low)}</td>
            <td class="text-right hide-mobile">${athDisplay}</td>
            <td class="text-right hide-mobile">${atlDisplay}</td>
        `;

        tbody.appendChild(row);
    });
}

// İstatistikleri güncelle
function updateStats(coins) {
    const totalElement = document.getElementById('totalCoins');
    const positiveElement = document.getElementById('positiveCount');
    const negativeElement = document.getElementById('negativeCount');
    
    if (totalElement) totalElement.textContent = coins.length;
    
    const positive = coins.filter(c => c.change > 0).length;
    const negative = coins.filter(c => c.change < 0).length;
    
    if (positiveElement) positiveElement.textContent = positive;
    if (negativeElement) negativeElement.textContent = negative;
}

// Son güncelleme zamanı
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('tr-TR', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    const element = document.getElementById('lastUpdate');
    if (element) {
        element.textContent = timeString;
    }
}

// Sayı formatlama
function formatNumber(num) {
    if (num >= 1000) {
        return num.toLocaleString('en-US', { 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 2 
        });
    } else if (num >= 1) {
        return num.toFixed(4);
    } else {
        return num.toFixed(6);
    }
}

// Coin arama
function filterCoins() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toUpperCase();
    
    let filtered = coinsData. filter(coin => 
        coin.symbol.includes(searchTerm)
    );

    // Mevcut filtreyi uygula
    if (currentFilter === 'gainers') {
        filtered = filtered.filter(c => c.change > 0);
    } else if (currentFilter === 'losers') {
        filtered = filtered.filter(c => c.change < 0);
    }

    filteredCoins = filtered;
    displayCoins(filteredCoins);
    updateStats(filteredCoins);
}

// Değişime göre filtrele
function filterByChange(type) {
    currentFilter = type;
    
    // Buton aktif durumunu güncelle
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Event'ten gelen butonu bul ve aktif yap
    const buttons = document.querySelectorAll('. filter-btn');
    buttons.forEach(btn => {
        if ((type === 'all' && btn.textContent.includes('All')) ||
            (type === 'gainers' && btn.textContent.includes('Gainers')) ||
            (type === 'losers' && btn.textContent.includes('Losers'))) {
            btn.classList.add('active');
        }
    });

    // Filtreyi uygula
    if (type === 'gainers') {
        filteredCoins = coinsData.filter(c => c.change > 0);
    } else if (type === 'losers') {
        filteredCoins = coinsData.filter(c => c.change < 0);
    } else {
        filteredCoins = [... coinsData];
    }

    displayCoins(filteredCoins);
    updateStats(filteredCoins);
}

// Tablo sıralama
function sortTable(column) {
    const direction = sortDirection[column];
    
    filteredCoins.sort((a, b) => {
        if (column === 'symbol') {
            return direction * a[column].localeCompare(b[column]);
        }
        
        // Null değerleri sona at
        if (a[column] === null && b[column] === null) return 0;
        if (a[column] === null) return 1;
        if (b[column] === null) return -1;
        
        return direction * (a[column] - b[column]);
    });

    sortDirection[column] *= -1;
    displayCoins(filteredCoins);
}

// Otomatik yenileme (60 saniye)
setInterval(() => {
    console.log('Auto-refresh triggered');
    loadData();
}, 60000);
