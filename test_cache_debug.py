#!/usr/bin/env python3
"""
Test Discord bot command and clear signal cache.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from datetime import datetime, timedelta

async def test_with_cache_clear():
    """Test analyzer while clearing old cache entries."""
    
    print("="*80)
    print("🧪 TEST DISCORD BOT WITH SIGNAL CACHE MANAGEMENT")
    print("="*80)
    print()
    
    config = Config()
    analyzer = MultiTimeframeAnalyzer(config)
    
    print("✓ Created new analyzer instance")
    print(f"  Previous signals cache is empty: {len(analyzer.previous_signals) == 0}")
    print()
    
    print("Testing single ticker: ETH-USD on all timeframes")
    print("-" * 80)
    
    total_signals = 0
    for timeframe in config.TIMEFRAMES:
        signal_data = await analyzer.analyze_ticker_timeframe('ETH-USD', timeframe)
        
        if signal_data:
            print(f"  {timeframe}: Found {signal_data['signal']} signal")
            print(f"     Sending to Discord...")
            
            # Send signal
            success = await analyzer.process_signal(signal_data)
            
            if success:
                print(f"     ✅ Sent to Discord!")
                total_signals += 1
            else:
                print(f"     ⊙ Blocked (duplicate sent within 5 min)")
        else:
            print(f"  {timeframe}: No signal")
    
    print()
    print(f"Total Signals Sent: {total_signals}")
    print()
    
    print("="*80)
    print("ℹ️  IMPORTANT: Signal Cache Info")
    print("="*80)
    print()
    print("The bot prevents duplicate signals within 5 minutes.")
    print("This is by design to avoid spam.")
    print()
    print("If you want to test again immediately:")
    print("  1. Change the ticker (test different coins)")
    print("  2. Change the timeframe")
    print("  3. Wait 5 minutes for cache to expire")
    print()
    print("Current cached signals:")
    for signal_key, timestamp in analyzer.previous_signals.items():
        age = datetime.now() - timestamp
        print(f"  {signal_key}: {age.seconds} seconds ago")
    print()

if __name__ == "__main__":
    asyncio.run(test_with_cache_clear())
