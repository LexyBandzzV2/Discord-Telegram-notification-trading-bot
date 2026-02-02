/**
 * n8n Trading Bot - Complete Indicator Logic
 * ===========================================
 * 
 * This JavaScript code replicates the Python trading bot's logic for use in n8n workflows.
 * 
 * FEATURES:
 * - Heikin-Ashi candle conversion
 * - Williams Alligator (13/8/5 SMMA)
 * - Stochastic Oscillator (14/3/3)
 * - Vortex Indicator (14 period)
 * - 3-point confirmation system
 * - Breakout candle validation
 * - Signal quality scoring
 * 
 * USAGE IN N8N:
 * 1. Add "Code" node (JavaScript)
 * 2. Copy this entire file
 * 3. Input: OHLCV data array
 * 4. Output: Signals with all indicators
 */

// =============================================================================
// HEIKIN-ASHI CONVERSION
// =============================================================================

/**
 * Convert standard OHLCV candles to Heikin-Ashi
 * @param {Array} candles - Array of {open, high, low, close, volume, timestamp}
 * @returns {Array} Heikin-Ashi candles with original data preserved
 */
function toHeikinAshi(candles) {
    if (!candles || candles.length < 2) {
        throw new Error('Need at least 2 candles for Heikin-Ashi conversion');
    }
    
    const haCandles = [];
    
    for (let i = 0; i < candles.length; i++) {
        const candle = candles[i];
        
        // HA Close = (O + H + L + C) / 4
        const haClose = (candle.open + candle.high + candle.low + candle.close) / 4;
        
        // HA Open = (Previous HA Open + Previous HA Close) / 2
        let haOpen;
        if (i === 0) {
            haOpen = candle.open; // First candle uses standard open
        } else {
            haOpen = (haCandles[i - 1].haOpen + haCandles[i - 1].haClose) / 2;
        }
        
        // HA High = Max(H, HA Open, HA Close)
        const haHigh = Math.max(candle.high, haOpen, haClose);
        
        // HA Low = Min(L, HA Open, HA Close)
        const haLow = Math.min(candle.low, haOpen, haClose);
        
        haCandles.push({
            // Original data
            origOpen: candle.open,
            origHigh: candle.high,
            origLow: candle.low,
            origClose: candle.close,
            volume: candle.volume,
            timestamp: candle.timestamp,
            // Heikin-Ashi data
            open: haOpen,
            high: haHigh,
            low: haLow,
            close: haClose,
            haOpen,
            haHigh,
            haLow,
            haClose
        });
    }
    
    return haCandles;
}

// =============================================================================
// TECHNICAL INDICATORS
// =============================================================================

/**
 * Calculate SMMA (Smoothed Moving Average)
 * Used for Williams Alligator
 */
function calculateSMMA(data, period) {
    const smma = [];
    let sum = 0;
    
    // Calculate first SMA
    for (let i = 0; i < period; i++) {
        sum += data[i];
    }
    smma[period - 1] = sum / period;
    
    // Calculate SMMA for remaining values
    for (let i = period; i < data.length; i++) {
        smma[i] = (smma[i - 1] * (period - 1) + data[i]) / period;
    }
    
    return smma;
}

/**
 * Calculate Williams Alligator (13/8/5 SMMA with Fibonacci shifts)
 */
function calculateAlligator(candles) {
    const closes = candles.map(c => c.close);
    
    // Calculate SMMA lines
    const jaw13 = calculateSMMA(closes, 13);   // Blue line
    const teeth8 = calculateSMMA(closes, 8);   // Red line
    const lips5 = calculateSMMA(closes, 5);    // Green line
    
    // Apply Fibonacci shifts
    const alligator = candles.map((candle, i) => ({
        jaw: i >= 8 ? jaw13[i - 8] : null,      // Shifted 8 bars forward
        teeth: i >= 5 ? teeth8[i - 5] : null,   // Shifted 5 bars forward
        lips: i >= 3 ? lips5[i - 3] : null      // Shifted 3 bars forward
    }));
    
    return alligator;
}

/**
 * Calculate Stochastic Oscillator (14/3/3)
 */
function calculateStochastic(candles, kPeriod = 14, kSmooth = 3, dSmooth = 3) {
    const stochastic = [];
    
    // Calculate %K
    const rawK = [];
    for (let i = kPeriod - 1; i < candles.length; i++) {
        const slice = candles.slice(i - kPeriod + 1, i + 1);
        const lowestLow = Math.min(...slice.map(c => c.low));
        const highestHigh = Math.max(...slice.map(c => c.high));
        const currentClose = candles[i].close;
        
        const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;
        rawK.push(k);
    }
    
    // Smooth %K
    const smoothK = [];
    for (let i = kSmooth - 1; i < rawK.length; i++) {
        const slice = rawK.slice(i - kSmooth + 1, i + 1);
        const avg = slice.reduce((a, b) => a + b, 0) / slice.length;
        smoothK.push(avg);
    }
    
    // Calculate %D (SMA of %K)
    const d = [];
    for (let i = dSmooth - 1; i < smoothK.length; i++) {
        const slice = smoothK.slice(i - dSmooth + 1, i + 1);
        const avg = slice.reduce((a, b) => a + b, 0) / slice.length;
        d.push(avg);
    }
    
    // Align arrays (pad with nulls)
    const offset = kPeriod + kSmooth + dSmooth - 3;
    for (let i = 0; i < candles.length; i++) {
        if (i < offset) {
            stochastic.push({ k: null, d: null });
        } else {
            const idx = i - offset;
            stochastic.push({
                k: smoothK[idx + dSmooth - 1] || null,
                d: d[idx] || null
            });
        }
    }
    
    return stochastic;
}

/**
 * Calculate Vortex Indicator (14 period)
 */
function calculateVortex(candles, period = 14) {
    const vortex = [];
    
    for (let i = period; i < candles.length; i++) {
        let vmPlus = 0;
        let vmMinus = 0;
        let trueRange = 0;
        
        for (let j = i - period + 1; j <= i; j++) {
            const current = candles[j];
            const prev = candles[j - 1];
            
            // Vortex Movement
            vmPlus += Math.abs(current.high - prev.low);
            vmMinus += Math.abs(current.low - prev.high);
            
            // True Range
            const tr = Math.max(
                current.high - current.low,
                Math.abs(current.high - prev.close),
                Math.abs(current.low - prev.close)
            );
            trueRange += tr;
        }
        
        vortex.push({
            viPlus: vmPlus / trueRange,
            viMinus: vmMinus / trueRange
        });
    }
    
    // Pad beginning with nulls
    const result = [];
    for (let i = 0; i < period; i++) {
        result.push({ viPlus: null, viMinus: null });
    }
    return result.concat(vortex);
}

// =============================================================================
// BREAKOUT CANDLE VALIDATION
// =============================================================================

/**
 * Check if candle is a valid breakout
 * Rules:
 * - Must be in top 3 longest candles (lookback period)
 * - NOT a doji (body < 10% of range)
 * - NOT smaller than previous candle
 * - Progressive growth pattern
 */
function isValidBreakoutCandle(candles, index, lookback = 3) {
    if (index < lookback) {
        return { isValid: false, reason: 'Insufficient data', rank: null };
    }
    
    const current = candles[index];
    const prev = candles[index - 1];
    
    // Calculate candle body sizes
    const currentBody = Math.abs(current.close - current.open);
    const prevBody = Math.abs(prev.close - prev.open);
    
    // Check 1: Is it a doji?
    const candleRange = current.high - current.low;
    if (candleRange > 0 && (currentBody / candleRange) < 0.1) {
        return { isValid: false, reason: 'Doji detected', rank: null };
    }
    
    // Check 2: Is current smaller than previous?
    if (currentBody < prevBody) {
        return { isValid: false, reason: 'Candle smaller than previous', rank: null };
    }
    
    // Check 3: Is it in top 3 longest candles?
    const recentBodies = [];
    for (let i = index - lookback + 1; i <= index; i++) {
        const body = Math.abs(candles[i].close - candles[i].open);
        recentBodies.push(body);
    }
    
    const sortedBodies = [...recentBodies].sort((a, b) => b - a);
    const rank = sortedBodies.indexOf(currentBody) + 1;
    
    if (rank <= 3) {
        // Check 4: Progressive growth
        let isProgressive = true;
        for (let i = 0; i < recentBodies.length - 1; i++) {
            if (recentBodies[i + 1] <= recentBodies[i]) {
                isProgressive = false;
                break;
            }
        }
        
        return {
            isValid: true,
            reason: isProgressive ? 'Valid breakout candle' : 'In top 3 but not fully progressive',
            rank
        };
    }
    
    return { isValid: false, reason: 'Not in top 3 longest candles', rank };
}

// =============================================================================
// POINT SYSTEM & SIGNAL GENERATION
// =============================================================================

/**
 * Generate trading signals with 3-point confirmation system
 * @param {Array} candles - Heikin-Ashi candles
 * @param {Boolean} enableBreakoutFilter - Apply breakout validation
 * @returns {Array} Candles with signals and all indicators
 */
function generateSignals(candles, enableBreakoutFilter = true) {
    // Calculate all indicators
    const alligator = calculateAlligator(candles);
    const stochastic = calculateStochastic(candles);
    const vortex = calculateVortex(candles);
    
    // Combine data
    const signals = candles.map((candle, i) => {
        const prevAlligator = i > 0 ? alligator[i - 1] : {};
        const prevStoch = i > 0 ? stochastic[i - 1] : {};
        const prevVortex = i > 0 ? vortex[i - 1] : {};
        
        const currentAlligator = alligator[i] || {};
        const currentStoch = stochastic[i] || {};
        const currentVortex = vortex[i] || {};
        
        // Initialize points
        let buyPoints = 0;
        let sellPoints = 0;
        
        // Track individual indicator signals
        const indicators = {
            alligatorBuy: false,
            alligatorSell: false,
            stochBuy: false,
            stochSell: false,
            vortexBuy: false,
            vortexSell: false
        };
        
        // Calculate mouth width
        const mouthWidth = currentAlligator.lips && currentAlligator.jaw
            ? Math.abs(currentAlligator.lips - currentAlligator.jaw)
            : 0;
        const mouthOpen = mouthWidth > (candle.close * 0.005); // 0.5% of price
        
        // =================================================================
        // INDICATOR 1: WILLIAMS ALLIGATOR
        // =================================================================
        
        // BUY: Lips crosses ABOVE Teeth AND Jaw (mouth wide open)
        if (
            prevAlligator.lips && prevAlligator.teeth &&
            currentAlligator.lips && currentAlligator.teeth && currentAlligator.jaw &&
            prevAlligator.lips <= prevAlligator.teeth &&
            currentAlligator.lips > currentAlligator.teeth &&
            currentAlligator.lips > currentAlligator.jaw &&
            mouthOpen
        ) {
            buyPoints++;
            indicators.alligatorBuy = true;
        }
        
        // SELL: Lips crosses BELOW Teeth AND Jaw (mouth wide open)
        if (
            prevAlligator.lips && prevAlligator.teeth &&
            currentAlligator.lips && currentAlligator.teeth && currentAlligator.jaw &&
            prevAlligator.lips >= prevAlligator.teeth &&
            currentAlligator.lips < currentAlligator.teeth &&
            currentAlligator.lips < currentAlligator.jaw &&
            mouthOpen
        ) {
            sellPoints++;
            indicators.alligatorSell = true;
        }
        
        // =================================================================
        // INDICATOR 2: STOCHASTIC OSCILLATOR
        // =================================================================
        
        // BUY: %K crosses ABOVE %D while BOTH above 80 (overbought momentum)
        if (
            prevStoch.k && prevStoch.d &&
            currentStoch.k && currentStoch.d &&
            prevStoch.k <= prevStoch.d &&
            currentStoch.k > currentStoch.d &&
            currentStoch.k > 80 &&
            currentStoch.d > 80
        ) {
            buyPoints++;
            indicators.stochBuy = true;
        }
        
        // SELL: %K crosses BELOW %D while BOTH below 20 (oversold momentum)
        if (
            prevStoch.k && prevStoch.d &&
            currentStoch.k && currentStoch.d &&
            prevStoch.k >= prevStoch.d &&
            currentStoch.k < currentStoch.d &&
            currentStoch.k < 20 &&
            currentStoch.d < 20
        ) {
            sellPoints++;
            indicators.stochSell = true;
        }
        
        // =================================================================
        // INDICATOR 3: VORTEX INDICATOR
        // =================================================================
        
        // BUY: VI+ crosses ABOVE VI- (uptrend strength)
        if (
            prevVortex.viPlus && prevVortex.viMinus &&
            currentVortex.viPlus && currentVortex.viMinus &&
            prevVortex.viPlus <= prevVortex.viMinus &&
            currentVortex.viPlus > currentVortex.viMinus
        ) {
            buyPoints++;
            indicators.vortexBuy = true;
        }
        
        // SELL: VI- crosses ABOVE VI+ (downtrend strength)
        if (
            prevVortex.viMinus && prevVortex.viPlus &&
            currentVortex.viMinus && currentVortex.viPlus &&
            prevVortex.viMinus <= prevVortex.viPlus &&
            currentVortex.viMinus > currentVortex.viPlus
        ) {
            sellPoints++;
            indicators.vortexSell = true;
        }
        
        // =================================================================
        // COMBINE SIGNALS (3 POINTS REQUIRED)
        // =================================================================
        
        const buySignalBase = buyPoints === 3;
        const sellSignalBase = sellPoints === 3;
        
        // Apply breakout filter
        let buySignal = buySignalBase;
        let sellSignal = sellSignalBase;
        let breakoutValid = false;
        let breakoutReason = '';
        let breakoutRank = null;
        
        if (enableBreakoutFilter && (buySignalBase || sellSignalBase)) {
            const breakout = isValidBreakoutCandle(candles, i, 3);
            breakoutValid = breakout.isValid;
            breakoutReason = breakout.reason;
            breakoutRank = breakout.rank;
            
            buySignal = buySignalBase && breakoutValid;
            sellSignal = sellSignalBase && breakoutValid;
        }
        
        // Calculate signal quality (0-1)
        let signalQuality = 0;
        if (buySignal || sellSignal) {
            signalQuality = (
                (breakoutRank ? breakoutRank / 3.0 : 0) * 0.4 + // 40% weight on candle rank
                (mouthOpen ? 1 : 0) * 0.3 + // 30% weight on alligator mouth
                0.3 // 30% base quality for 3-point confirmation
            );
        }
        
        // Determine final entry signal
        let entrySignal = 0;
        if (buySignal) entrySignal = 1;
        if (sellSignal) entrySignal = -1;
        
        return {
            ...candle,
            // Indicators
            alligatorJaw: currentAlligator.jaw,
            alligatorTeeth: currentAlligator.teeth,
            alligatorLips: currentAlligator.lips,
            mouthWidth,
            mouthOpen,
            stochK: currentStoch.k,
            stochD: currentStoch.d,
            vortexPlus: currentVortex.viPlus,
            vortexMinus: currentVortex.viMinus,
            // Points
            buyPoints,
            sellPoints,
            // Individual signals
            ...indicators,
            // Breakout validation
            breakoutValid,
            breakoutReason,
            breakoutRank,
            // Final signals
            buySignalBase,
            sellSignalBase,
            buySignal,
            sellSignal,
            entrySignal,
            signalQuality
        };
    });
    
    return signals;
}

// =============================================================================
// N8N WORKFLOW EXECUTION
// =============================================================================

/**
 * Main function for n8n Code node
 * Processes incoming OHLCV data and returns signals
 */

// Get input data from n8n
// Expected input format: Array of {open, high, low, close, volume, timestamp}
const inputData = $input.all();

// Extract OHLCV array from first item
const ohlcvData = inputData[0].json.data || inputData[0].json;

if (!Array.isArray(ohlcvData) || ohlcvData.length < 20) {
    throw new Error('Need at least 20 candles for analysis');
}

// Configuration (can be passed from n8n inputs)
const config = {
    enableBreakoutFilter: $input.first().json.enableBreakoutFilter ?? true,
    minSignalQuality: $input.first().json.minSignalQuality ?? 0.5
};

// Step 1: Convert to Heikin-Ashi
const haCandles = toHeikinAshi(ohlcvData);

// Step 2: Generate signals
const signals = generateSignals(haCandles, config.enableBreakoutFilter);

// Step 3: Filter for actual entry signals
const entrySignals = signals.filter(s => s.entrySignal !== 0 && s.signalQuality >= config.minSignalQuality);

// Step 4: Format output
const output = {
    totalCandles: signals.length,
    totalSignals: entrySignals.length,
    buySignals: entrySignals.filter(s => s.entrySignal === 1).length,
    sellSignals: entrySignals.filter(s => s.entrySignal === -1).length,
    signals: entrySignals.map(s => ({
        timestamp: s.timestamp,
        signalType: s.entrySignal === 1 ? 'BUY' : 'SELL',
        price: s.close,
        volume: s.volume,
        quality: s.signalQuality,
        breakoutRank: s.breakoutRank,
        indicators: {
            alligator: {
                jaw: s.alligatorJaw,
                teeth: s.alligatorTeeth,
                lips: s.alligatorLips,
                mouthOpen: s.mouthOpen
            },
            stochastic: {
                k: s.stochK,
                d: s.stochD
            },
            vortex: {
                plus: s.vortexPlus,
                minus: s.vortexMinus
            }
        },
        points: {
            buy: s.buyPoints,
            sell: s.sellPoints
        }
    })),
    latestSignal: entrySignals.length > 0 ? entrySignals[entrySignals.length - 1] : null
};

// Return formatted output for n8n
return output;
