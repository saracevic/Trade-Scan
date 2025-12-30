let coinsData = [];
let filteredCoins = [];
let currentFilter = 'all';
let sortDirection = {
    symbol: 1,
    price: 1,
    change: 1,
    asianRangeFib: 1
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
        statusElement.style.color = 'var(--color-positive)';
    }
}

// Asian Range %50 Fib hesapla (Son Cuma'nın Asian Session: 00:00-08:00 UTC)
function calculateAsianRangeFib(klines) {
    if (!klines || klines.length === 0) return null;
    
    // Son Cuma'yı bul - daha esnek yaklaşım
    let lastFridayCandles = [];
    let currentDate = new Date();
    let searchDays = 0;
    
    // Son 14 gün içinde Cuma ara
    for (let i = klines.length - 1; i >= 0 && searchDays < 14; i--) {
        const timestamp = klines[i][0];
        const date = new Date(timestamp);
        const dayOfWeek = date.getUTCDay();
        const hour = date.getUTCHours();
        
        // Cuma günü (5) - tüm saatler
        if (dayOfWeek === 5) {
            // Asian Session saatleri tercih et ama yoksa tüm günü al
            if (hour >= 0 && hour < 8) {
                lastFridayCandles.push(klines[i]);
            } else if (lastFridayCandles.length === 0) {
                // Asian session verisi yoksa normal Cuma verilerini al
                lastFridayCandles.push(klines[i]);
            }
        }
        
        searchDays++;
    }
    
    // Eğer Cuma bulunamadıysa, son 8 saatlik veriyi al (fallback)
    if (lastFridayCandles.length < 3) {
        console.warn('Friday not found, using last 8 hours as fallback');
        lastFridayCandles = klines.slice(-8);
    }
    
    if (lastFridayCandles.length === 0) {
        console.warn('No valid candle data found');
        return null;
    }
    
    // Asian Session için Body High/Low hesapla
    let bodyHigh = -Infinity;
    let bodyLow = Infinity;
    
    lastFridayCandles.forEach(candle => {
        const open = parseFloat(candle[1]);
        const close = parseFloat(candle[4]);
        
        // Body = Open ve Close arasındaki max/min
        const candleBodyHigh = Math.max(open, close);
        const candleBodyLow = Math.min(open, close);
        
        bodyHigh = Math.max(bodyHigh, candleBodyHigh);
        bodyLow = Math.min(bodyLow, candleBodyLow);
    });
    
    // Geçerli değer kontrolü
    if (bodyHigh === -Infinity || bodyLow === Infinity || bodyHigh <= 0 || bodyLow <= 0) {
        console.warn('Invalid body high/low values');
        return null;
    }
    
    // 50% Fibonacci (midpoint)
    const asianRangeFib50 = (bodyHigh + bodyLow) / 2;
    
    console.log(`✓ Asian Fib: High=${bodyHigh.toFixed(4)}, Low=${bodyLow.toFixed(4)}, 50%=${asianRangeFib50.toFixed(4)}, Candles=${lastFridayCandles.length}`);
    
    return asianRangeFib50;
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
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        console.log('Fetching Binance data...');
        
        // Binance Futures 24hr ticker
        const binanceResponse = await fetch('https://fapi.binance.com/fapi/v1/ticker/24hr', {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);

        if (!binanceResponse.ok) {
            throw new Error(`Binance API error: ${binanceResponse.status}`);
        }

        const binanceData = await binanceResponse.json();
        console.log('Binance data received:', binanceData.length, 'items');
        
        // USDT perpetual futures filtrele
        const futuresCoins = binanceData
            .filter(coin => coin.symbol.endsWith('USDT'))
            .map(coin => ({
                symbol: coin.symbol.replace('USDT', ''),
                price: parseFloat(coin.lastPrice),
                change: parseFloat(coin.priceChangePercent),
                volume: parseFloat(coin.volume),
                asianRangeFib: null
            }));

        console.log('Filtered coins:', futuresCoins.length);

        // Asian Range %50 Fib hesaplamaları (paralel, batch processing)
        console.log('Calculating Asian Range 50% Fib for all pairs...');
        
        // Tüm coinler için hesapla, ancak batch'ler halinde (rate limit için)
        const batchSize = 20;
        const batches = [];
        
        for (let i = 0; i < Math.min(futuresCoins.length, 200); i += batchSize) {
            batches.push(futuresCoins.slice(i, i + batchSize));
        }
        
        for (const batch of batches) {
            const promises = batch.map(async coin => {
                try {
                    const symbol = coin.symbol + 'USDT';
                    const klineResponse = await fetch(
                        `https://fapi.binance.com/fapi/v1/klines?symbol=${symbol}&interval=1h&limit=336`,
                        { timeout: 5000 }
                    );
                    
                    if (klineResponse.ok) {
                        const klines = await klineResponse.json();
                        const asianFib = calculateAsianRangeFib(klines);
                        
                        if (asianFib && asianFib > 0) {
                            coin.asianRangeFib = asianFib;
                        } else {
                            console.warn(`❌ ${coin.symbol}: Invalid Asian Fib calculated`);
                        }
                    } else {
                        console.warn(`❌ ${coin.symbol}: API error ${klineResponse.status}`);
                    }
                } catch (err) {
                    console.warn(`❌ ${coin.symbol}: ${err.message}`);
                }
            });
            
            await Promise.all(promises);
            // Rate limit için kısa bekleme
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log(`✓ Asian Range calculated for ${futuresCoins.filter(c => c.asianRangeFib).length} coins`);

        coinsData = futuresCoins;
        filteredCoins = [...coinsData];

        // Varsayılan sıralama: değişime göre
        coinsData.sort((a, b) => b.change - a.change);
        filteredCoins.sort((a, b) => b.change - a.change);

        console.log('Displaying coins...');
        displayCoins(filteredCoins);
        updateStats(coinsData);
        updateLastUpdateTime();

        if (loading) loading.style.display = 'none';
        if (table) table.style.display = 'block';
        
        console.log('Data loaded successfully!');

    } catch (err) {
        console.error('Error loading data:', err);
        
        if (loading) loading.style.display = 'none';
        if (error) {
            error.style.display = 'block';
            const errorText = error.querySelector('p');
            if (errorText) {
                if (err.name === 'AbortError') {
                    errorText.textContent = '⏱️ Request timeout. Please check your connection and try again.';
                } else {
                    errorText.textContent = `❌ ${err.message}. Please try again.`;
                }
            }
        }
    }
}

// Coinleri tabloda göster
function displayCoins(coins) {
    const tbody = document.getElementById('coinsBody');
    if (!tbody) {
        console.error('Table body not found!');
        return;
    }
    
    tbody.innerHTML = '';

    if (coins.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--text-secondary);">No coins found</td></tr>';
        return;
    }

    coins.forEach(coin => {
        const row = document.createElement('tr');
        
        const changeClass = coin.change > 0 ? 'positive-change' : 
                           coin.change < 0 ? 'negative-change' : 'neutral-change';
        const changeSymbol = coin.change > 0 ? '+' : '';

        // Asian Range Fib gösterimi
        let asianFibDisplay = '<span style="color: var(--text-muted);">-</span>';
        let asianFibDistDisplay = '<span style="color: var(--text-muted);">-</span>';
        
        if (coin.asianRangeFib && coin.asianRangeFib > 0) {
            asianFibDisplay = `<span class="asian-fib-value">$${formatNumber(coin.asianRangeFib)}</span>`;
            
            // Current Price ile Asian Range Fib arasındaki % mesafe
            const distPercent = ((coin.price - coin.asianRangeFib) / coin.asianRangeFib) * 100;
            const distClass = distPercent >= 0 ? 'positive-change' : 'negative-change';
            const distSymbol = distPercent >= 0 ? '+' : '';
            asianFibDistDisplay = `<span class="percent-badge ${distClass}">${distSymbol}${distPercent.toFixed(2)}%</span>`;
        }

        row.innerHTML = `
            <td class="sticky-col"><div class="coin-symbol">${coin.symbol}</div></td>
            <td class="text-right price">$${formatNumber(coin.price)}</td>
            <td class="text-right"><span class="change ${changeClass}">${changeSymbol}${coin.change.toFixed(2)}%</span></td>
            <td class="text-right asian-col">${asianFibDisplay}</td>
            <td class="text-right">${asianFibDistDisplay}</td>
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
    
    let filtered = coinsData.filter(coin => 
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
    
    const buttons = document.querySelectorAll('.filter-btn');
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
        filteredCoins = [...coinsData];
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
