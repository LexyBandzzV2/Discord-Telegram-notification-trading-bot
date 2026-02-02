"""
Quick test script to analyze multiple volatile instruments
and see which ones have recent trading signals
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from close_knit import TradingBot

# Instruments to test
INSTRUMENTS = {
    "ES=F": "S&P 500 E-mini Futures",
    "NQ=F": "NASDAQ-100 E-mini Futures",
    "YM=F": "Dow Jones E-mini Futures",
    "SPY": "S&P 500 ETF",
    "QQQ": "NASDAQ-100 ETF",
    "TSLA": "Tesla",
    "GME": "GameStop",
    "AMC": "AMC Entertainment",
    "NVDA": "NVIDIA"
}

print("\n" + "="*70)
print("TESTING MULTIPLE VOLATILE INSTRUMENTS")
print("="*70)

results = []

for ticker, name in INSTRUMENTS.items():
    print(f"\n{'='*70}")
    print(f"Testing: {ticker} ({name})")
    print(f"{'='*70}")
    
    try:
        bot = TradingBot(
            ticker=ticker,
            start_date="2024-01-01",
            end_date=None,
            enable_breakout_filter=False,  # More signals
            verbose=False  # Less output
        )
        
        # Run analysis
        if bot.fetch_data() and bot.convert_to_heikin_ashi() and bot.calculate_signals():
            signals = bot.signal_data[bot.signal_data['ENTRY_SIGNAL'] != 0]
            
            if not signals.empty:
                buy_count = (signals['ENTRY_SIGNAL'] == 1).sum()
                sell_count = (signals['ENTRY_SIGNAL'] == -1).sum()
                
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'total_signals': len(signals),
                    'buy_signals': buy_count,
                    'sell_signals': sell_count,
                    'last_signal_date': signals.index[-1],
                    'last_signal_type': 'BUY' if signals.iloc[-1]['ENTRY_SIGNAL'] == 1 else 'SELL'
                })
                
                print(f"✓ Found {len(signals)} signals!")
                print(f"  BUY: {buy_count} | SELL: {sell_count}")
                print(f"  Last signal: {results[-1]['last_signal_type']} on {results[-1]['last_signal_date']}")
            else:
                print(f"✗ No signals found")
        else:
            print(f"✗ Analysis failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")

# Summary
print(f"\n\n{'='*70}")
print("SUMMARY - INSTRUMENTS WITH SIGNALS")
print(f"{'='*70}\n")

if results:
    results.sort(key=lambda x: x['total_signals'], reverse=True)
    
    print(f"{'Ticker':<10} {'Name':<30} {'Total':<8} {'BUY':<6} {'SELL':<6} {'Last Signal'}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['ticker']:<10} {r['name']:<30} {r['total_signals']:<8} {r['buy_signals']:<6} {r['sell_signals']:<6} {r['last_signal_type']}")
    
    print(f"\n✓ {len(results)} instruments generated signals!")
    print(f"\nBEST CHOICE: {results[0]['ticker']} ({results[0]['name']}) with {results[0]['total_signals']} signals")
else:
    print("✗ No instruments generated signals in this period.")
    print("\nTry:")
    print("  • Extending the date range")
    print("  • Using shorter timeframe data (1h, 15m)")
    print("  • Adjusting indicator parameters")

print(f"\n{'='*70}\n")
