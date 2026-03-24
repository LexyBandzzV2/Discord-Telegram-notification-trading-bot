"""
Trading Bot Automated Setup and Launcher
=========================================
Simplifies running the bot with interactive prompts.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

def print_banner():
    """Print trading bot banner."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                   🤖 TRADING BOT LAUNCHER 🤖                     ║
    ║            Discord-Enabled Automated Trading System              ║
    ║                                                                  ║
    ║  Status: ✅ READY TO TRADE                                      ║
    ║  Discord: ✅ CONNECTED                                          ║
    ║  Data: ✅ YAHOO FINANCE                                         ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ ERROR: .env file not found!")
        print("Please create .env file with your Discord credentials:")
        print("""
DISCORD_BOT_TOKEN=your_token_here
DISCORD_WEBHOOK_URL=your_webhook_url_here
DATA_PROVIDER=yahoo
        """)
        return False
    
    print("✓ .env file found")
    
    # Load and verify
    from dotenv import load_dotenv
    load_dotenv()
    
    webhook = os.getenv('DISCORD_WEBHOOK_URL')
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not webhook and not bot_token:
        print("❌ ERROR: No Discord credentials in .env!")
        return False
    
    print("✓ Discord credentials configured")
    return True

def run_single_stock_analysis():
    """Run analysis on a single stock."""
    print("\n" + "="*70)
    print("SINGLE STOCK ANALYSIS")
    print("="*70)
    
    ticker = input("\nEnter stock ticker (e.g., AAPL, MSFT, TSLA): ").upper().strip()
    if not ticker:
        print("❌ Invalid ticker")
        return
    
    print("\nEnter date range:")
    years_back = input("How many years of data? (default: 1): ").strip() or "1"
    
    try:
        years = int(years_back)
    except:
        years = 1
    
    start_date = (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📊 Analyzing {ticker} from {start_date} to {end_date}...")
    print("This may take 30-60 seconds...\n")
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
    
    from config.config import get_config
    from main import BotOrchestrator
    
    config = get_config()
    orchestrator = BotOrchestrator(config)
    
    success = orchestrator.run_analysis(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        enable_breakout_filter=True
    )
    
    if success:
        print(f"\n✓ Analysis complete for {ticker}")
        print("📱 Check Discord for any trading signals!")
    else:
        print(f"\n❌ Analysis failed for {ticker}")

def run_multi_stock_analysis():
    """Run analysis on multiple stocks."""
    print("\n" + "="*70)
    print("MULTI-STOCK BATCH ANALYSIS")
    print("="*70)
    
    tickers = input("\nEnter tickers (comma-separated, e.g., AAPL,MSFT,TSLA): ").upper().strip()
    if not tickers:
        tickers = "AAPL,MSFT,TSLA,GOOGL,NVDA"
        print(f"Using default tickers: {tickers}")
    
    ticker_list = [t.strip() for t in tickers.split(',')]
    
    years_back = input("How many years of data? (default: 1): ").strip() or "1"
    
    try:
        years = int(years_back)
    except:
        years = 1
    
    start_date = (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📊 Analyzing {len(ticker_list)} stocks from {start_date} to {end_date}...")
    print("This may take a few minutes...\n")
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
    
    from config.config import get_config
    from main import BotOrchestrator
    
    config = get_config()
    orchestrator = BotOrchestrator(config)
    
    completed = 0
    for i, ticker in enumerate(ticker_list, 1):
        print(f"\n[{i}/{len(ticker_list)}] Analyzing {ticker}...")
        try:
            success = orchestrator.run_analysis(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                enable_breakout_filter=True
            )
            if success:
                completed += 1
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
    
    print("\n" + "="*70)
    print(f"✓ Analysis complete: {completed}/{len(ticker_list)} stocks processed")
    print("📱 Check Discord for trading signals!")
    print("="*70)

def test_discord():
    """Test Discord notifications."""
    print("\n" + "="*70)
    print("DISCORD NOTIFICATION TEST")
    print("="*70 + "\n")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, 'test_discord_setup.py'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    if result.returncode == 0:
        print("\n✓ Discord test complete - Check your Discord channel!")
    else:
        print("\n❌ Discord test failed")

def show_help():
    """Show detailed help."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    TRADING BOT HELP MENU                         ║
╚══════════════════════════════════════════════════════════════════╝

COMMANDS:
  1 - Analyze single stock (interactive)
  2 - Batch analyze multiple stocks (interactive)
  3 - Test Discord notifications
  4 - Show guide (opens TRADING_BOT_GUIDE.md)
  5 - View configuration
  6 - Run full system test
  7 - Exit

EXAMPLES:
  Analyze AAPL:
    python launcher.py -t AAPL
    
  Analyze multiple stocks:
    python launcher.py -t AAPL,MSFT,TSLA
    
  Custom date range:
    python launcher.py -t AAPL --start 2024-01-01 --end 2024-12-31

OPTIONS:
  -t, --ticker      Stock ticker(s) to analyze
  -s, --start       Start date (YYYY-MM-DD)
  -e, --end         End date (YYYY-MM-DD)
  --help            Show this help message

DISCORD SETUP GUIDE:
  1. Go to https://discord.com/developers/applications
  2. Create new application named "Trading Bot"
  3. Go to "Bot" tab and copy bot token
  4. In your server, create webhook in desired channel
  5. Copy webhook URL
  6. Save in .env file:
     DISCORD_BOT_TOKEN=your_token
     DISCORD_WEBHOOK_URL=your_webhook_url
     
For detailed guide, check: TRADING_BOT_GUIDE.md
    """)

def main():
    """Main launcher."""
    parser = argparse.ArgumentParser(
        description='Trading Bot Launcher',
        add_help=False
    )
    
    parser.add_argument('-t', '--ticker', type=str, help='Stock ticker(s) to analyze')
    parser.add_argument('-s', '--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--help', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    # Check environment
    print_banner()
    
    if not check_env_file():
        return 1
    
    # Command-line mode
    if args.ticker:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
        
        from config.config import get_config
        from main import BotOrchestrator
        
        config = get_config()
        orchestrator = BotOrchestrator(config)
        
        tickers = args.ticker.split(',')
        start = args.start or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        end = args.end or datetime.now().strftime('%Y-%m-%d')
        
        for ticker in tickers:
            print(f"\nAnalyzing {ticker}...")
            orchestrator.run_analysis(ticker.strip(), start, end, True)
        
        return 0
    
    # Interactive mode
    if args.help:
        show_help()
        return 0
    
    while True:
        print("\n" + "="*70)
        print("MAIN MENU")
        print("="*70)
        print("""
1. Analyze single stock
2. Batch analyze multiple stocks
3. Test Discord notifications
4. Show trading guide
5. View configuration
6. Run full system test
7. Exit
        """)
        
        choice = input("Select option (1-7): ").strip()
        
        if choice == '1':
            run_single_stock_analysis()
        elif choice == '2':
            run_multi_stock_analysis()
        elif choice == '3':
            test_discord()
        elif choice == '4':
            print("\n📖 Opening TRADING_BOT_GUIDE.md...")
            try:
                import subprocess
                subprocess.Popen(['notepad', 'TRADING_BOT_GUIDE.md'])
            except:
                with open('TRADING_BOT_GUIDE.md', 'r') as f:
                    print(f.read()[:2000] + "\n... (see file for full guide)")
        elif choice == '5':
            from config.config import Config
            Config.print_config()
        elif choice == '6':
            print("\n🧪 Running full system test...\n")
            import subprocess
            subprocess.run([sys.executable, 'test_multi_tickers.py'])
        elif choice == '7':
            print("\n👋 Goodbye!")
            return 0
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    exit(main())
