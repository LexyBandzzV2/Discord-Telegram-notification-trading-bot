#!/usr/bin/env python3
"""
Test that all timeframes are fetching data properly.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer

async def test_all_timeframes():
    """Test data fetching for all timeframes."""
    
    print("="*80)
    print("📊 DATA FETCH TEST - All Timeframes")
    print("="*80)
    print()
    
    config = Config()
    analyzer = MultiTimeframeAnalyzer(config)
    
    ticker = 'AAPL'
    print(f"Testing: {ticker}")
    print()
    print("Lookback Settings:")
    for tf, days in config.TIMEFRAME_LOOKBACK.items():
        print(f"  {tf}: {days} days")
    print()
    print("-" * 80)
    print()
    
    for timeframe in config.TIMEFRAMES:
        print(f"Testing {timeframe}:")
        signal_data = await analyzer.analyze_ticker_timeframe(ticker, timeframe)
        
        if signal_data:
            print(f"  ✅ Signal: {signal_data['signal']} @ ${signal_data['price']:.2f}")
        print()

if __name__ == "__main__":
    asyncio.run(test_all_timeframes())
