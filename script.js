let coinsData = [];
let filteredCoins = [];
let currentFilter = 'all';
let sortDirection = {
    symbol: 1,
    price: 1,
    change: 1,
    asianRangeFib: 1
};

// Asian Range değerlerini sakla (haftalık güncellenir)
let cachedAsianRanges = {};
let lastAsianRangeUpdate = null;
let isCalculatingAsianRange = false;

// Sayfa yüklendiğinde
window.addEventListener('load', () => {
    console.log('Page loaded, starting data fetch...');
    loadCachedAsianRanges();
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

// Asian Range cache'i localStorage'dan yükle
function loadCachedAsianRanges() {
    try {
        const stored = localStorage.getItem('asianRanges');
        const storedDate = localStorage.getItem('asianRangeDate');
        
        if (stored && storedDate) {
            cachedAsianRanges = JSON.parse(stored);
            lastAsianRangeUpdate = new Date(storedDate);
            console.log(`✓ Loaded ${Object.keys(cachedAsianRanges).length} cached Asian Ranges from ${lastAsianRangeUpdate.toLocaleString()}`);
        }
    } catch (err) {
        console.warn('Failed to load cached Asian Ranges:', err);
    }
}

// Asian Range değerlerini localStorage'a kaydet
function saveAsianRangesToCache() {
    try {
        localStorage.setItem('asianRanges', JSON.stringify(cachedAsianRanges));
        localStorage.setItem('asianRangeDate', new Date().toISOString());
        console.log(`✓ Saved ${Object.keys(cachedAsianRanges).length} Asian Ranges to cache`);
    } catch (err) {
        console.warn('Failed to save Asian Ranges:', err);
    }
}

// Yeni Asian Range hesaplaması gerekli mi kontrol et
function shouldUpdateAsianRange() {
    if (!lastAsianRangeUpdate) return true;
    
    const now = new Date();
    const lastUpdate = new Date(lastAsianRangeUpdate);
    
    // Son güncelleme 7 günden eskiyse güncelle
    const daysDiff = (now - lastUpdate) / (1000 * 60 * 60 * 24);
    
    return daysDiff >= 7;
}

// Asian Range %50 Fib hesapla (Perşembe 19:00-00:00 New York saati)
function calculateAsianRangeFib(klines) {
    if (!klines || klines.length === 0) return null;
    
    // Son Perşembe'yi bul (New York saatine göre 19:00-00:00)
    let thursdayCandles = [];
    let foundThursday = false;
    
    for (let i = klines.length - 1; i >= 0; i--) {
        const timestamp = klines[i][0];
        const date = new Date(timestamp);
        
        // UTC saatini New York saatine çevir (UTC-5)
        const nyHour = (date.getUTCHours() - 5 + 24) % 24;
        const nyDate = new Date(date.getTime() - (5 * 60 * 60 * 1000));
        const nyDayOfWeek = nyDate.getDay();
        
        // Perşembe günü (4) ve NY saati 19:00-23:59
        if (nyDayOfWeek === 4) {
            foundThursday = true;
            if (nyHour >= 19 && nyHour <= 23) {
                thursdayCandles.push(klines[i]);
            }
        } else if (foundThursday && nyDayOfWeek !== 4) {
            break;
        }
    }
    
    if (thursdayCandles.length < 3) {
        console.warn('Not enough Thursday data, using fallback');
        // Fallback: son 5 saatlik data
        thursdayCandles = klines.slice(-5);
    }
    
    if (thursdayCandles.length === 0) {
        return null;
    }
    
    // Body High/Low hesapla
    let bodyHigh = -Infinity;
    let bodyLow = Infinity;
    
    thursdayCandles.forEach(candle => {
        const open = parseFloat(candle[1]);
        const close = parseFloat(candle[4]);
        
        const candleBodyHigh = Math.max(open, close);
        const candleBodyLow = Math.min(open, close);
        
        bodyHigh = Math.max(bodyHigh, candleBodyHigh);
        bodyLow = Math.min(bodyLow, candleBodyLow);
    });
    
    if (bodyHigh === -Infinity || bodyLow === Infinity || bodyHigh <= 0 || bodyLow <= 0) {
        return null;
    }
    
    // 50% Fibonacci (midpoint)
    const asianRangeFib50 = (bodyHigh + bodyLow) / 2;
    
    return asianRangeFib50;
}

// Tüm coinler için Asian Range hesapla (background'da çalışır)
async function calculateAllAsianRanges(coins) {
    if (isCalculatingAsianRange) {
        console.log('Asian Range calculation already in progress...');
        return;
    }
    
    isCalculatingAsianRange = true;
    console.log('🔄 Starting Asian Range calculation for all coins...');
    
    let calculated = 0;
    const total = coins.length;
    
    // Her coin için sırayla hesapla (rate limit önlemi)
    for (let i = 0; i < total; i++) {
        const coin = coins[i];
        
        try {
            const symbol = coin.symbol + 'USDT';
            
            // API isteği
            const klineResponse = await fetch(
                `https://fapi.binance.com/fapi/v1/klines?symbol=${symbol}&interval=1h&limit=336`
            );
            
            if (klineResponse.ok) {
                const klines = await klineResponse.json();
                const asianFib = calculateAsianRangeFib(klines);
                
                if (asianFib && asianFib > 0) {
                    cachedAsianRanges[coin.symbol] = asianFib;
                    coin.asianRangeFib = asianFib;
                    calculated++;
                    
                    // Her 10 hesaplamada bir güncelle
                    if (calculated % 10 === 0) {
                        console.log(`📊 Progress: ${calculated}/${total} (${((calculated/total)*100).toFixed(1)}%)`);
                        // UI'ı güncelle
                        displayCoins([...filteredCoins]);
                        saveAsianRangesToCache();
                    }
                }
            }
            
            // Rate limit için bekleme (50ms)
            await new Promise(resolve => setTimeout(resolve, 50));
            
        } catch (err) {
            console.warn(`❌ ${coin.symbol}: ${err.message}`);
        }
    }
    
    lastAsianRangeUpdate = new Date();
    saveAsianRangesToCache();
    isCalculatingAsianRange = false;
    
    console.log(`✅ Asian Range calculation completed: ${calculated}/${total} coins`);
    
    // Final update
    displayCoins([...filteredCoins]);
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
        
        const binanceResponse = await fetch('https://fapi.binance.com/fapi/v1/ticker/24hr', {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);

        if (!binanceResponse.ok) {
            throw new Error(`Binance API error: ${binanceResponse.status}`);
        }

        const binanceData = await binanceResponse.json();
        console.log('Binance data received:', binanceData.length, 'items');
        
        const futuresCoins = binanceData
            .filter(coin => coin.symbol.endsWith('USDT'))
            .map(coin => ({
                symbol: coin.symbol.replace('USDT', ''),
                price: parseFloat(coin.lastPrice),
                change: parseFloat(coin.priceChangePercent),
                volume: parseFloat(coin.volume),
                asianRangeFib: cachedAsianRanges[coin.symbol.replace('USDT', '')] || null
            }));

        console.log('Filtered coins:', futuresCoins.length);

        coinsData = futuresCoins;
        filteredCoins = [...coinsData];

        coinsData.sort((a, b) => b.change - a.change);
        filteredCoins.sort((a, b) => b.change - a.change);

        displayCoins(filteredCoins);
        updateStats(coinsData);
        updateLastUpdateTime();

        if (loading) loading.style.display = 'none';
        if (table) table.style.display = 'block';
        
        console.log('Data loaded successfully!');

        // Asian Range güncelleme gerekli mi?
        const needsUpdate = shouldUpdateAsianRange();
        
        if (needsUpdate && !isCalculatingAsianRange) {
            console.log('⏰ Starting Asian Range calculation in background...');
            // Background'da hesapla (UI'ı bloklamadan)
            setTimeout(() => {
                calculateAllAsianRanges(coinsData);
            }, 1000);
        } else if (isCalculatingAsianRange) {
            console.log('⏳ Asian Range calculation in progress...');
        } else {
            console.log(`✓ Using cached Asian Range values from ${lastAsianRangeUpdate.toLocaleString()}`);
        }

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

        let asianFibDisplay = '<span style="color: var(--text-muted); font-size: 11px;">Calculating...</span>';
        let asianFibDistDisplay = '<span style="color: var(--text-muted);">-</span>';
        
        if (coin.asianRangeFib && coin.asianRangeFib > 0) {
            asianFibDisplay = `<span class="asian-fib-value">$${formatNumber(coin.asianRangeFib)}</span>`;
            
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

function filterCoins() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toUpperCase();
    
    let filtered = coinsData.filter(coin => 
        coin.symbol.includes(searchTerm)
    );

    if (currentFilter === 'gainers') {
        filtered = filtered.filter(c => c.change > 0);
    } else if (currentFilter === 'losers') {
        filtered = filtered.filter(c => c.change < 0);
    }

    filteredCoins = filtered;
    displayCoins(filteredCoins);
    updateStats(filteredCoins);
}

function filterByChange(type) {
    currentFilter = type;
    
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

function sortTable(column) {
    const direction = sortDirection[column];
    
    filteredCoins.sort((a, b) => {
        if (column === 'symbol') {
            return direction * a[column].localeCompare(b[column]);
        }
        
        if (a[column] === null && b[column] === null) return 0;
        if (a[column] === null) return 1;
        if (b[column] === null) return -1;
        
        return direction * (a[column] - b[column]);
    });

    sortDirection[column] *= -1;
    displayCoins(filteredCoins);
}

// Otomatik yenileme (60 saniye) - sadece fiyatları günceller
setInterval(() => {
    if (!isCalculatingAsianRange) {
        console.log('Auto-refresh: Updating prices only');
        loadData();
    }
}, 60000);
