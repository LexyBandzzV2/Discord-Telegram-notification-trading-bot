#!/usr/bin/env python3
"""
Test script to display detailed indicator formatting in Discord messages.
"""

import asyncio
import json
from src.discord_notifier import DiscordNotifier, SignalType
from config.config import Config

async def test_detailed_indicators():
    """Test the detailed indicator formatting."""
    
    config = Config()
    notifier = DiscordNotifier(
        bot_token=config.DISCORD_BOT_TOKEN,
        channels=config.DISCORD_CHANNELS
    )
    
    # Example BUY signal with detailed indicators
    buy_indicators = {
        'price': 397.10,
        'stoch_k': 75.5,
        'stoch_d': 72.3,
        'stoch_status': 'Overbought (touching 80+ line)',
        'alligator_status': 'Green line crossing upward over red line and blue line',
        'vortex_status': 'Green cross - VI+ crossing above VI- (uptrend)'
    }
    
    # Create embed for BUY signal
    embed_buy = notifier._create_embed(
        signal_type=SignalType.BUY,
        ticker='TSLA',
        ticker_display='🚗 Tesla',
        price=397.10,
        timeframe='1h',
        confidence=0.88,
        indicators=buy_indicators
    )
    
    print("=" * 80)
    print("🟢 BUY SIGNAL - Discord Embed Format")
    print("=" * 80)
    print(json.dumps(embed_buy, indent=2))
    print()
    
    # Example SELL signal with different indicators
    sell_indicators = {
        'price': 62978.68,
        'stoch_k': 18.5,
        'stoch_d': 22.1,
        'stoch_status': 'Oversold (touching 20- line)',
        'alligator_status': 'Green line crossing downward below red line and blue line',
        'vortex_status': 'Red cross - VI- crossing above VI+ (downtrend)'
    }
    
    # Create embed for SELL signal
    embed_sell = notifier._create_embed(
        signal_type=SignalType.SELL,
        ticker='BTC-USD',
        ticker_display='₿ Bitcoin',
        price=62978.68,
        timeframe='15m',
        confidence=0.87,
        indicators=sell_indicators
    )
    
    print("=" * 80)
    print("🔴 SELL SIGNAL - Discord Embed Format")
    print("=" * 80)
    print(json.dumps(embed_sell, indent=2))
    print()
    
    # Example with mid-range stochastic
    mid_indicators = {
        'price': 275.92,
        'stoch_k': 55.3,
        'stoch_d': 52.7,
        'stoch_status': 'Mid-Range (K:55.3, D:52.7)',
        'alligator_status': 'Green line above red and blue lines',
        'vortex_status': 'Green cross - VI+ above VI+ (uptrend)'
    }
    
    # Create embed
    embed_mid = notifier._create_embed(
        signal_type=SignalType.BUY,
        ticker='AAPL',
        ticker_display='🍎 Apple',
        price=275.92,
        timeframe='1h',
        confidence=0.80,
        indicators=mid_indicators
    )
    
    print("=" * 80)
    print("🟢 BUY SIGNAL with Mid-Range Stochastic")
    print("=" * 80)
    print(json.dumps(embed_mid, indent=2))
    print()
    
    print("=" * 80)
    print("✅ Indicator Formatting Test Complete")
    print("=" * 80)
    print()
    print("DETAILED INDICATOR DESCRIPTIONS:")
    print()
    print("📊 Stochastic RSI:")
    print("  • 'Overbought (touching 80+ line)' - When %K or %D >= 80")
    print("  • 'Oversold (touching 20- line)' - When %K or %D <= 20")
    print("  • 'Mid-Range (K:X.X, D:X.X)' - When between 20 and 80")
    print()
    print("🐊 Alligator (Green/Red/Blue Lines):")
    print("  BUY: 'Green line crossing upward over [red line][and/or blue line]'")
    print("  SELL: 'Green line crossing downward below [red line][and/or blue line]'")
    print()
    print("🌪️  Vortex:")
    print("  BUY: 'Green cross - VI+ [crossing above/above] VI- (uptrend)'")
    print("  SELL: 'Red cross - VI- [crossing above/above] VI+ (downtrend)'")
    print()

if __name__ == "__main__":
    asyncio.run(test_detailed_indicators())
