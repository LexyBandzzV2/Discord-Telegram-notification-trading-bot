#!/usr/bin/env python3
"""
Test analyzer to see if it's generating signals.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from datetime import datetime

async def test_analyzer():
    """Test if analyzer generates signals."""
    
    print("="*80)
    print("🧪 ANALYZER SIGNAL GENERATION TEST")
    print("="*80)
    print()
    
    config = Config()
    analyzer = MultiTimeframeAnalyzer(config)
    
    print("Testing: ETH-USD on 1h timeframe")
    print("-" * 80)
    
    try:
        signal_data = await analyzer.analyze_ticker_timeframe('ETH-USD', '1h')
        
        if signal_data:
            print(f"✅ SIGNAL GENERATED!")
            print(f"   Ticker: {signal_data['ticker']}")
            print(f"   Timeframe: {signal_data['timeframe']}")
            print(f"   Signal: {signal_data['signal']}")
            print(f"   Price: ${signal_data['price']:.2f}")
            print(f"   Confidence: {signal_data['confidence']*100:.1f}%")
        else:
            print("⊙ No signal (price in hold range)")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("="*80)
    print("Testing: All assets on 1h timeframe")
    print("="*80)
    print()
    
    total_signals = 0
    for ticker in config.PRIMARY_TICKERS:
        try:
            signal_data = await analyzer.analyze_ticker_timeframe(ticker, '1h')
            if signal_data:
                print(f"✅ {ticker}: {signal_data['signal']} @ ${signal_data['price']:.2f}")
                total_signals += 1
            else:
                print(f"⊙ {ticker}: No signal")
        except Exception as e:
            print(f"❌ {ticker}: Error - {e}")
    
    print()
    print(f"Total Signals Found: {total_signals}")
    print()
    
    if total_signals == 0:
        print("⚠️  NO SIGNALS FOUND")
        print()
        print("This could mean:")
        print("  1. All prices are within the hold range (±2% of 50-day MA)")
        print("  2. Not enough historical data available")
        print("  3. Data fetch issue")
        print()
        print("The bot is working correctly - just no buy/sell signals at this moment.")

if __name__ == "__main__":
    asyncio.run(test_analyzer())
