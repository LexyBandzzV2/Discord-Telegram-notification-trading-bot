import pandas as pd
import ta
import numpy as np


def is_valid_breakout_candle(df: pd.DataFrame, idx: int, lookback: int = 3) -> dict:
    """
    Validates if a candle meets your breakout criteria:
    - Must be one of the 3 longest candles in recent lookback period
    - Each candle should be progressively larger than the previous
    - NOT a doji (close ≈ open)
    - NOT smaller than previous candle
    
    Returns dict with: {'is_valid': bool, 'reason': str, 'candle_rank': int}
    """
    if idx < lookback:
        return {'is_valid': False, 'reason': 'Insufficient data', 'candle_rank': None}
    
    # Calculate candle body size (absolute difference between close and open)
    current_body = abs(df['Close'].iloc[idx] - df['Open'].iloc[idx])
    prev_body = abs(df['Close'].iloc[idx-1] - df['Open'].iloc[idx-1])
    
    # Get recent candle bodies for comparison
    recent_bodies = []
    for i in range(idx - lookback + 1, idx + 1):
        body_size = abs(df['Close'].iloc[i] - df['Open'].iloc[i])
        recent_bodies.append(body_size)
    
    # Check 1: Is it a doji? (body is less than 10% of the range)
    candle_range = df['High'].iloc[idx] - df['Low'].iloc[idx]
    if candle_range > 0 and (current_body / candle_range) < 0.1:
        return {'is_valid': False, 'reason': 'Doji detected', 'candle_rank': None}
    
    # Check 2: Is current candle smaller than previous?
    if current_body < prev_body:
        return {'is_valid': False, 'reason': 'Candle smaller than previous', 'candle_rank': None}
    
    # Check 3: Is it one of the 3 longest candles?
    sorted_bodies = sorted(recent_bodies, reverse=True)
    candle_rank = sorted_bodies.index(current_body) + 1 if current_body in sorted_bodies else None
    
    if candle_rank and candle_rank <= 3:
        # Check 4: Progressive growth pattern (each candle bigger than previous)
        is_progressive = True
        for i in range(len(recent_bodies) - 1):
            if recent_bodies[i+1] <= recent_bodies[i]:
                is_progressive = False
                break
        
        if is_progressive:
            return {'is_valid': True, 'reason': 'Valid breakout candle', 'candle_rank': candle_rank}
        else:
            return {'is_valid': True, 'reason': 'In top 3 but not fully progressive', 'candle_rank': candle_rank}
    
    return {'is_valid': False, 'reason': 'Not in top 3 longest candles', 'candle_rank': candle_rank}


def detect_market_structure(df: pd.DataFrame, idx: int, lookback: int = 20) -> dict:
    """
    Detects potential Head & Shoulders or inverse H&S patterns.
    Returns structure info for ML feature engineering.
    
    This is simplified - for production, you'd use ML pattern recognition.
    """
    if idx < lookback:
        return {'pattern': None, 'confidence': 0}
    
    recent_highs = df['High'].iloc[idx-lookback:idx+1]
    recent_lows = df['Low'].iloc[idx-lookback:idx+1]
    
    # Simple volatility and trend detection
    high_volatility = recent_highs.std() > recent_highs.mean() * 0.02
    price_range = recent_highs.max() - recent_lows.min()
    
    # Detect if we're near a significant high/low (potential shoulder area)
    current_high = df['High'].iloc[idx]
    current_low = df['Low'].iloc[idx]
    
    near_resistance = current_high >= recent_highs.quantile(0.90)
    near_support = current_low <= recent_lows.quantile(0.10)
    
    structure = {
        'high_volatility': high_volatility,
        'near_resistance': near_resistance,
        'near_support': near_support,
        'price_range': price_range,
        'pattern': 'consolidation' if not high_volatility else 'volatile'
    }
    
    return structure


def generate_signals(df: pd.DataFrame, enable_breakout_filter: bool = True) -> pd.DataFrame:
    """
    Calculates all indicators and generates trade signals based on:
    1. Williams Alligator (trend direction & mouth open/closed)
    2. Stochastic Oscillator (momentum confirmation)
    3. Vortex Indicator (directional movement confirmation)
    4. Breakout candle validation (size, progression, not doji)
    5. Market structure (for ML features)
    
    Parameters:
    - df: Heikin-Ashi OHLCV DataFrame
    - enable_breakout_filter: If True, only signals on valid breakout candles
    
    Returns:
    - DataFrame with signals and all indicator columns
    """
    
    # --- Indicator Calculation (on HA data) ---
    
    # 1. Williams Alligator (13, 8, 5 with Fibonacci shifts)
    # Manual calculation using SMMA (Smoothed Moving Average)
    # JAW (Blue) - 13 SMMA shifted 8 bars
    # TEETH (Red) - 8 SMMA shifted 5 bars
    # LIPS (Green) - 5 SMMA shifted 3 bars
    
    def smma(series, period):
        """Smoothed Moving Average (SMMA)"""
        return series.ewm(alpha=1/period, adjust=False).mean()
    
    df['ALLIGATOR_JAW'] = smma(df['Close'], 13).shift(8)
    df['ALLIGATOR_TEETH'] = smma(df['Close'], 8).shift(5)
    df['ALLIGATOR_LIPS'] = smma(df['Close'], 5).shift(3)
    
    # 2. Stochastic Oscillator (14, 3, 3 default)
    # Using ta library
    from ta.momentum import StochasticOscillator
    stoch = StochasticOscillator(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        window=14,
        smooth_window=3
    )
    df['STOCHk_14_3_3'] = stoch.stoch()  # %K line
    df['STOCHd_14_3_3'] = stoch.stoch_signal()  # %D line
    
    # 3. Vortex Indicator (14 period default)
    # Using ta library
    from ta.trend import VortexIndicator
    vortex = VortexIndicator(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        window=14
    )
    df['VIp_14'] = vortex.vortex_indicator_pos()  # Positive line
    df['VIm_14'] = vortex.vortex_indicator_neg()  # Negative line
    
    # 4. Additional helpful indicators for context
    from ta.volatility import AverageTrueRange
    atr = AverageTrueRange(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        window=14
    )
    df['ATRr_14'] = atr.average_true_range()
    
    # --- Define Column Names ---
    LIPS = 'ALLIGATOR_LIPS'
    TEETH = 'ALLIGATOR_TEETH'
    JAW = 'ALLIGATOR_JAW'
    STOCH_K = 'STOCHk_14_3_3'
    STOCH_D = 'STOCHd_14_3_3'
    VI_POS = 'VIp_14'
    VI_NEG = 'VIm_14'
    
    # Drop NaN rows from indicator calculation
    df = df.dropna()
    df = df.reset_index(drop=False)  # Keep datetime index as column
    
    # =========================================================================
    # POINT SYSTEM FOR SIGNAL CONFIRMATION
    # Each indicator contributes points when conditions are met
    # Total of 3 points required for entry (all indicators must align)
    # =========================================================================
    
    # Initialize point columns
    df['BUY_POINTS'] = 0
    df['SELL_POINTS'] = 0
    
    # Initialize individual indicator signals for tracking
    df['ALLIGATOR_BUY'] = False
    df['ALLIGATOR_SELL'] = False
    df['STOCH_BUY'] = False
    df['STOCH_SELL'] = False
    df['VORTEX_BUY'] = False
    df['VORTEX_SELL'] = False
    
    # Calculate mouth width (distance between Lips and Jaw)
    df['MOUTH_WIDTH'] = abs(df[LIPS] - df[JAW])
    df['MOUTH_OPEN'] = df['MOUTH_WIDTH'] > (df['Close'] * 0.005)  # Mouth open = 0.5% of price
    
    # =========================================================================
    # INDICATOR 1: WILLIAMS ALLIGATOR (Green Line Crosses)
    # =========================================================================
    
    # BUY: Green (Lips) crosses ABOVE Red (Teeth) AND Blue (Jaw)
    # - Mouth must be VERY WIDE open
    # - Lips > Teeth AND Lips > Jaw (bullish alignment)
    alligator_buy_cross = (
        (df[LIPS].shift(1) <= df[TEETH].shift(1)) &  # Was below or equal
        (df[LIPS] > df[TEETH]) &                      # Crosses above
        (df[LIPS] > df[JAW]) &                        # Also above Jaw
        df['MOUTH_OPEN']                              # Mouth is wide open
    )
    
    # SELL: Green (Lips) crosses BELOW Red (Teeth) AND Blue (Jaw)
    # - Mouth must be VERY WIDE open
    # - Lips < Teeth AND Lips < Jaw (bearish alignment)
    alligator_sell_cross = (
        (df[LIPS].shift(1) >= df[TEETH].shift(1)) &  # Was above or equal
        (df[LIPS] < df[TEETH]) &                      # Crosses below
        (df[LIPS] < df[JAW]) &                        # Also below Jaw
        df['MOUTH_OPEN']                              # Mouth is wide open
    )
    
    # Award points
    df.loc[alligator_buy_cross, 'BUY_POINTS'] += 1
    df.loc[alligator_buy_cross, 'ALLIGATOR_BUY'] = True
    df.loc[alligator_sell_cross, 'SELL_POINTS'] += 1
    df.loc[alligator_sell_cross, 'ALLIGATOR_SELL'] = True
    
    # =========================================================================
    # INDICATOR 2: STOCHASTIC OSCILLATOR (Blue Line Crosses Orange)
    # =========================================================================
    
    # BUY: Blue (%K) crosses ABOVE Orange (%D) WHILE ABOVE 80 line
    # - %K crosses above %D (blue crosses orange)
    # - Both must be above 80 (overbought zone = strong momentum)
    stoch_buy_cross = (
        (df[STOCH_K].shift(1) <= df[STOCH_D].shift(1)) &  # %K was below %D
        (df[STOCH_K] > df[STOCH_D]) &                      # %K crosses above %D
        (df[STOCH_K] > 80) &                               # %K above 80 line
        (df[STOCH_D] > 80)                                 # %D also above 80
    )
    
    # SELL: Blue (%K) crosses BELOW Orange (%D) WHILE BELOW 20 line
    # - %K crosses below %D (blue crosses below orange)
    # - Both must be below 20 (oversold zone = strong downward momentum)
    stoch_sell_cross = (
        (df[STOCH_K].shift(1) >= df[STOCH_D].shift(1)) &  # %K was above %D
        (df[STOCH_K] < df[STOCH_D]) &                      # %K crosses below %D
        (df[STOCH_K] < 20) &                               # %K below 20 line
        (df[STOCH_D] < 20)                                 # %D also below 20
    )
    
    # Award points
    df.loc[stoch_buy_cross, 'BUY_POINTS'] += 1
    df.loc[stoch_buy_cross, 'STOCH_BUY'] = True
    df.loc[stoch_sell_cross, 'SELL_POINTS'] += 1
    df.loc[stoch_sell_cross, 'STOCH_SELL'] = True
    
    # =========================================================================
    # INDICATOR 3: VORTEX INDICATOR (Red vs Green Line)
    # =========================================================================
    
    # BUY: Green (VI+) crosses ABOVE Red (VI-)
    # - Positive vortex crosses above negative vortex
    # - Indicates upward trend strength
    vortex_buy_cross = (
        (df[VI_POS].shift(1) <= df[VI_NEG].shift(1)) &  # VI+ was below VI-
        (df[VI_POS] > df[VI_NEG])                        # VI+ crosses above VI-
    )
    
    # SELL: Red (VI-) crosses ABOVE Green (VI+)
    # - Negative vortex crosses above positive vortex
    # - Indicates downward trend strength
    vortex_sell_cross = (
        (df[VI_NEG].shift(1) <= df[VI_POS].shift(1)) &  # VI- was below VI+
        (df[VI_NEG] > df[VI_POS])                        # VI- crosses above VI+
    )
    
    # Award points
    df.loc[vortex_buy_cross, 'BUY_POINTS'] += 1
    df.loc[vortex_buy_cross, 'VORTEX_BUY'] = True
    df.loc[vortex_sell_cross, 'SELL_POINTS'] += 1
    df.loc[vortex_sell_cross, 'VORTEX_SELL'] = True
    
    # =========================================================================
    # COMBINE SIGNALS - ALL 3 INDICATORS MUST ALIGN (3 POINTS)
    # =========================================================================
    
    df['BUY_SIGNAL_BASE'] = (df['BUY_POINTS'] == 3)
    df['SELL_SIGNAL_BASE'] = (df['SELL_POINTS'] == 3)
    
    # --- Apply Breakout Candle Filter ---
    if enable_breakout_filter:
        df['BREAKOUT_VALID'] = False
        df['BREAKOUT_REASON'] = ''
        df['BREAKOUT_RANK'] = 0
        
        for idx in range(3, len(df)):
            result = is_valid_breakout_candle(df, idx, lookback=3)
            df.at[idx, 'BREAKOUT_VALID'] = result['is_valid']
            df.at[idx, 'BREAKOUT_REASON'] = result['reason']
            df.at[idx, 'BREAKOUT_RANK'] = result['candle_rank'] if result['candle_rank'] else 0
        
        # Only trigger signals on valid breakout candles
        df['BUY_SIGNAL'] = df['BUY_SIGNAL_BASE'] & df['BREAKOUT_VALID']
        df['SELL_SIGNAL'] = df['SELL_SIGNAL_BASE'] & df['BREAKOUT_VALID']
    else:
        df['BUY_SIGNAL'] = df['BUY_SIGNAL_BASE']
        df['SELL_SIGNAL'] = df['SELL_SIGNAL_BASE']
    
    # --- Market Structure Analysis (for ML features) ---
    df['STRUCTURE_PATTERN'] = ''
    df['NEAR_RESISTANCE'] = False
    df['NEAR_SUPPORT'] = False
    df['HIGH_VOLATILITY'] = False
    
    for idx in range(20, len(df)):
        structure = detect_market_structure(df, idx, lookback=20)
        df.at[idx, 'STRUCTURE_PATTERN'] = structure['pattern']
        df.at[idx, 'NEAR_RESISTANCE'] = structure['near_resistance']
        df.at[idx, 'NEAR_SUPPORT'] = structure['near_support']
        df.at[idx, 'HIGH_VOLATILITY'] = structure['high_volatility']
    
    # --- Final Entry Signal (1 = Buy, -1 = Sell, 0 = No Trade) ---
    df['ENTRY_SIGNAL'] = 0
    df.loc[df['BUY_SIGNAL'], 'ENTRY_SIGNAL'] = 1
    df.loc[df['SELL_SIGNAL'], 'ENTRY_SIGNAL'] = -1
    
    # --- Calculate Signal Quality Score (for ML training) ---
    df['SIGNAL_QUALITY'] = 0.0
    
    # Higher quality when:
    # - Breakout candle is in top 3 (if filter enabled)
    # - High volatility environment
    # - Near key support/resistance levels
    
    if enable_breakout_filter and 'BREAKOUT_RANK' in df.columns:
        df.loc[df['ENTRY_SIGNAL'] != 0, 'SIGNAL_QUALITY'] = (
            (df['BREAKOUT_RANK'].fillna(0) / 3.0) * 0.4 +  # 40% weight on candle rank
            df['HIGH_VOLATILITY'].astype(int) * 0.3 +       # 30% weight on volatility
            (df['NEAR_RESISTANCE'] | df['NEAR_SUPPORT']).astype(int) * 0.3  # 30% weight on structure
        )
    else:
        df.loc[df['ENTRY_SIGNAL'] != 0, 'SIGNAL_QUALITY'] = (
            df['HIGH_VOLATILITY'].astype(int) * 0.5 +       # 50% weight on volatility
            (df['NEAR_RESISTANCE'] | df['NEAR_SUPPORT']).astype(int) * 0.5  # 50% weight on structure
        )
    
    return df


# --- ML Feature Engineering Helper ---
def prepare_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares features for machine learning model to predict Head & Shoulders
    and improve signal quality.
    
    Features include:
    - Price action (candle patterns, momentum)
    - Indicator values and crosses
    - Market structure
    - Volume profile
    - Time-based features (market open, etc.)
    """
    ml_df = df.copy()
    
    # Time-based features (if index is datetime)
    if 'Date' in ml_df.columns or isinstance(ml_df.index, pd.DatetimeIndex):
        date_col = ml_df.index if isinstance(ml_df.index, pd.DatetimeIndex) else ml_df['Date']
        ml_df['HOUR'] = date_col.hour
        ml_df['IS_MARKET_OPEN'] = (ml_df['HOUR'] >= 9) & (ml_df['HOUR'] <= 10)  # First hour
        ml_df['DAY_OF_WEEK'] = date_col.dayofweek
    
    # Price momentum features
    ml_df['PRICE_CHANGE_PCT'] = ml_df['Close'].pct_change()
    ml_df['VOLATILITY_RATIO'] = ml_df['ATRr_14'] / ml_df['Close']  # Normalized ATR
    
    # Candle pattern features
    ml_df['CANDLE_BODY'] = abs(ml_df['Close'] - ml_df['Open'])
    ml_df['CANDLE_RANGE'] = ml_df['High'] - ml_df['Low']
    ml_df['BODY_TO_RANGE'] = ml_df['CANDLE_BODY'] / (ml_df['CANDLE_RANGE'] + 1e-10)
    
    # Indicator strength features
    ml_df['ALLIGATOR_SEPARATION'] = abs(ml_df['ALLIGATOR_LIPS'] - ml_df['ALLIGATOR_JAW'])
    ml_df['VORTEX_DIFF'] = abs(ml_df['VIp_14'] - ml_df['VIm_14'])
    ml_df['STOCH_MOMENTUM'] = ml_df['STOCHk_14_3_3'] - ml_df['STOCHd_14_3_3']
    
    return ml_df


# --- Example Usage ---
if __name__ == "__main__":
    print("Indicators module loaded successfully!")
    print("\nAvailable functions:")
    print("- generate_signals(df, enable_breakout_filter=True)")
    print("- is_valid_breakout_candle(df, idx, lookback=3)")
    print("- detect_market_structure(df, idx, lookback=20)")
    print("- prepare_ml_features(df)")

    print("\n" + "="*60)
    print("PARAMETER TUNING GUIDE:")
# --- Example Usage ---
if __name__ == "__main__":
    print("Indicators module loaded successfully!")
    print("\nAvailable functions:")
    print("- generate_signals(df, enable_breakout_filter=True)")
    print("- is_valid_breakout_candle(df, idx, lookback=3)")
    print("- detect_market_structure(df, idx, lookback=20)")
    print("- prepare_ml_features(df)")
    print("\n" + "="*60)
    print("PARAMETER TUNING GUIDE:")
    print("="*60)
    print("\n1. enable_breakout_filter parameter:")
    print("   True  (Recommended) - Only signals on valid breakout candles")
    print("   False (Relaxed)     - Signals whenever indicators align")
    print("\n2. To use in your script:")
    print("   ha_df = generate_signals(ha_df, enable_breakout_filter=True)")
    print("\n3. To adjust lookback periods, edit the function code:")
    print("   Line 231: is_valid_breakout_candle(df, idx, lookback=3)")
    print("   Line 249: detect_market_structure(df, idx, lookback=20)")
    print("="*60) 

    #COME BACK TO THIS
# paramters: valid breakout
# generate_signals(df, enable_breakout_filter=True)  # Strict mode
# generate_signals(df, enable_breakout_filter=False) -  Relaxed mode

# True - (Recommended): Only gives you signals on valid breakout candles 
# (follows your 3-candle rule, rejects dojis, etc.)

# False - Gives signals whenever indicators align, even on weak candles
