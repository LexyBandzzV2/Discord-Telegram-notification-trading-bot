"""
Trading Strategy Parameters
============================
Defines the trading strategy parameters used by the bot.
These parameters are passed to the LLM for strategy suggestions
and daily summaries so the AI understands your methodology.

Strategy: Triple Indicator Confirmation (Alligator + Stochastic + Vortex)
"""


def get_strategy_params() -> dict:
    """
    Get the trading strategy parameters.
    
    Returns:
        Dictionary with strategy name, indicators, entry rules,
        and risk management parameters.
    """
    return {
        "name": "Triple Indicator Confirmation Strategy",
        "description": (
            "A momentum-based strategy that requires all 3 indicators "
            "(Williams Alligator, Stochastic Oscillator, and Vortex Indicator) "
            "to align before generating an entry signal. Optional breakout "
            "candle filter for higher-quality entries."
        ),
        "indicators": {
            "Williams Alligator": {
                "type": "Trend Direction & Momentum",
                "jaw_period": 13,
                "jaw_shift": 8,
                "teeth_period": 8,
                "teeth_shift": 5,
                "lips_period": 5,
                "lips_shift": 3,
                "smoothing": "SMMA (Smoothed Moving Average)",
                "buy_condition": "Green (Lips) crosses ABOVE Red (Teeth) AND Blue (Jaw), mouth wide open (>0.5% of price)",
                "sell_condition": "Green (Lips) crosses BELOW Red (Teeth) AND Blue (Jaw), mouth wide open",
            },
            "Stochastic Oscillator": {
                "type": "Momentum Confirmation",
                "k_period": 14,
                "d_period": 3,
                "smooth_window": 3,
                "overbought_level": 80,
                "oversold_level": 20,
                "buy_condition": "%K crosses above %D while BOTH above 80 (strong upward momentum)",
                "sell_condition": "%K crosses below %D while BOTH below 20 (strong downward momentum)",
            },
            "Vortex Indicator": {
                "type": "Directional Movement Confirmation",
                "period": 14,
                "buy_condition": "VI+ (green) crosses above VI- (red) → uptrend confirmed",
                "sell_condition": "VI- (red) crosses above VI+ (green) → downtrend confirmed",
            },
        },
        "entry_rules": [
            "ALL 3 indicators must align (3 points required for entry)",
            "BUY: Alligator bullish cross + Stochastic overbought cross + Vortex bullish cross",
            "SELL: Alligator bearish cross + Stochastic oversold cross + Vortex bearish cross",
            "Optional breakout filter: candle must be in top 3 longest of recent 3, progressive growth, not a doji",
            "Minimum confidence threshold: 60%",
        ],
        "timeframes": ["1m", "5m", "15m", "1h"],
        "assets": [
            "TSLA (Tesla)", "BTC-USD (Bitcoin)", "AAPL (Apple)",
            "ETH-USD (Ethereum)", "^GSPC (S&P 500)", "XRP-USD (XRP)",
            "NVDA (NVIDIA)", "GLD (Gold)", "SLV (Silver)"
        ],
        "risk_management": {
            "signal_deduplication": "5 minute cooldown between same signals",
            "min_data_bars": "Minimum 5 valid bars required for analysis",
            "nan_handling": "Drop NaN rows after indicator calculation",
            "breakout_filter": "Optional - rejects dojis, requires progressive candle growth",
            "confidence_scoring": "Based on price deviation from 50-period average",
        },
        "market_structure": {
            "volatility_detection": "High volatility if std > 2% of mean price",
            "support_resistance": "Near resistance if price >= 90% of recent high, near support if <= 10% of recent low",
            "pattern": "Consolidation vs volatile regime detection",
        },
    }
