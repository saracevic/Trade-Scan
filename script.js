// Asian Range %50 Fib hesapla (Son Cuma'nın Asian Session: 00:00-08:00 UTC)
function calculateAsianRangeFib(klines) {
    if (!klines || klines.length === 0) return null;
    
    // Son Cuma'yı bul
    let lastFridayCandles = [];
    let foundFriday = false;
    
    for (let i = klines.length - 1; i >= 0; i--) {
        const timestamp = klines[i][0];
        const date = new Date(timestamp);
        const dayOfWeek = date.getUTCDay();
        const hour = date.getUTCHours();
        
        // Cuma günü (5) ve Asian Session saatleri (00:00-08:00 UTC)
        if (dayOfWeek === 5) {
            foundFriday = true;
            if (hour >= 0 && hour < 8) {
                lastFridayCandles.push(klines[i]);
            }
        } else if (foundFriday) {
            // Cuma'yı geçtik, dur
            break;
        }
    }
    
    if (lastFridayCandles.length === 0) {
        console.warn('No Friday Asian Session data found');
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
    
    // 50% Fibonacci (midpoint)
    const asianRangeFib50 = (bodyHigh + bodyLow) / 2;
    
    console.log(`Asian Range Fib: High=${bodyHigh.toFixed(4)}, Low=${bodyLow.toFixed(4)}, 50%=${asianRangeFib50.toFixed(4)}, Candles=${lastFridayCandles.length}`);
    
    return asianRangeFib50;
}
