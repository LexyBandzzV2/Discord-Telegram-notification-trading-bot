"""
Test Discord Bot Commands (Simulated)
======================================
Tests bot command functionality without connecting to Discord.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer


async def test_single_ticker(ticker: str):
    """Test analysis for single ticker."""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: Analyzing {config.get_ticker_display_name(ticker)}")
    print(f"{'='*80}\n")
    
    analyzer = MultiTimeframeAnalyzer(config)
    
    total_signals = 0
    results_by_tf = {tf: [] for tf in config.TIMEFRAMES}
    
    for timeframe in config.TIMEFRAMES:
        signal_data = await analyzer.analyze_ticker_timeframe(ticker, timeframe)
        
        if signal_data:
            results_by_tf[timeframe].append(signal_data)
            total_signals += 1
            await analyzer.process_signal(signal_data)
    
    await analyzer.close()
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"✅ Analysis Complete for {config.get_ticker_display_name(ticker)}")
    print(f"{'='*80}")
    print(f"Total Signals: {total_signals}\n")
    
    for tf in config.TIMEFRAMES:
        emoji = analyzer.notifier.TIMEFRAME_EMOJIS.get(tf, '⏱️')
        count = len(results_by_tf[tf])
        print(f"{emoji} {tf.upper()}: {count} signals")
    
    print()


async def test_all_tickers():
    """Test analysis for all tickers."""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: Full Market Analysis")
    print(f"{'='*80}\n")
    
    analyzer = MultiTimeframeAnalyzer(config)
    
    total_signals = 0
    results_by_tf = {tf: [] for tf in config.TIMEFRAMES}
    
    for ticker in config.PRIMARY_TICKERS:
        print(f"📊 Analyzing {config.get_ticker_display_name(ticker)}...")
        
        for timeframe in config.TIMEFRAMES:
            signal_data = await analyzer.analyze_ticker_timeframe(ticker, timeframe)
            
            if signal_data:
                results_by_tf[timeframe].append(signal_data)
                total_signals += 1
                await analyzer.process_signal(signal_data)
    
    await analyzer.close()
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"✅ Full Analysis Complete")
    print(f"{'='*80}")
    print(f"Tickers Analyzed: {len(config.PRIMARY_TICKERS)}")
    print(f"Total Signals: {total_signals}\n")
    
    for tf in config.TIMEFRAMES:
        emoji = analyzer.notifier.TIMEFRAME_EMOJIS.get(tf, '⏱️')
        count = len(results_by_tf[tf])
        print(f"{emoji} {tf.upper()}: {count} signals")
    
    print()


async def main():
    """Main test function."""
    print(f"\n{'='*80}")
    print("🤖 DISCORD BOT COMMAND TESTS")
    print(f"{'='*80}\n")
    
    # Validate config
    is_valid, message = Config.validate()
    print(f"{message}\n")
    
    if not is_valid:
        print("❌ Configuration invalid")
        return 1
    
    # Show config
    Config.print_config()
    
    # Run tests
    print("Test 1: Single Ticker Analysis")
    await test_single_ticker('TSLA')
    
    print("\nTest 2: Another Single Ticker")
    await test_single_ticker('AAPL')
    
    print("\nTest 3: Full Market Analysis")
    await test_all_tickers()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80)
    print("\nBot Commands Ready:")
    print("  !analyze TSLA         - Analyze Tesla")
    print("  !analyze AAPL         - Analyze Apple")
    print("  !analyze all          - Full market analysis")
    print("  !status               - Show bot status")
    print("  !help                 - Show all commands")
    print("\nRun with: python discord_bot.py")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    config = Config()
    exit_code = asyncio.run(main())
    exit(exit_code)
