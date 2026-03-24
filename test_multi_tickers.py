"""
Multi-Ticker Trading Bot Test
==============================
Tests the trading bot across multiple stocks and shows real trading signals.
"""

import sys
import os
from datetime import datetime, timedelta

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config, get_config
from main import BotOrchestrator

def test_multiple_tickers():
    """Test trading bot across multiple tickers."""
    
    # Load configuration
    config = get_config()
    
    # List of popular tickers to test
    test_tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'NVDA']
    
    # Date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print("\n" + "="*80)
    print("TRADING BOT - MULTI-TICKER ANALYSIS WITH DISCORD NOTIFICATIONS")
    print("="*80)
    print(f"Testing {len(test_tickers)} stocks over {(datetime.now() - datetime.strptime(start_date, '%Y-%m-%d')).days} days")
    print(f"Date Range: {start_date} to {end_date}")
    print("="*80 + "\n")
    
    # Create orchestrator
    orchestrator = BotOrchestrator(config)
    
    # Test each ticker
    for i, ticker in enumerate(test_tickers, 1):
        print(f"\n[{i}/{len(test_tickers)}] ANALYZING {ticker}...")
        print("-" * 80)
        
        try:
            success = orchestrator.run_analysis(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                enable_breakout_filter=True
            )
            
            if success:
                print(f"✓ {ticker} analysis complete")
            else:
                print(f"✗ {ticker} analysis failed")
                
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
    
    print("\n" + "="*80)
    print("BATCH ANALYSIS COMPLETE")
    print("="*80)
    print("\n📊 Check your Discord channel for notifications of any signals found!")
    print("📈 Multiple timeframes and indicators were analyzed for each stock.\n")


if __name__ == "__main__":
    test_multiple_tickers()
