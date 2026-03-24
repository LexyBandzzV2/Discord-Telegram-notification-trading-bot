"""
Main Trading Bot Entry Point
=============================
Orchestrates the complete trading bot workflow with Discord notifications.

Usage:
    python main.py --ticker AAPL --start 2024-01-01 --provider yahoo
    python main.py --config config.json

Environment Setup:
    1. Create a .env file in the project root:
       DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
       (OR)
       DISCORD_BOT_TOKEN=your_bot_token
       DISCORD_CHANNEL_ID=your_channel_id
       DATA_PROVIDER=yahoo
    
    2. Install dependencies:
       pip install -r requirements.txt
    
    3. Run the bot:
       python main.py --ticker AAPL
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Optional

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

# Import modules
from config.config import Config, get_config
from src.data_fetcher import DataFetcher

# Import TradingBot from main file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "trading_bot",
    os.path.join(os.path.dirname(__file__), "src", "Trading Bot Brain. regular.py")
)
trading_bot_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trading_bot_module)
TradingBot = trading_bot_module.TradingBot

# Import Discord notifier
from src.discord_notifier import DiscordNotifier, SignalType


class BotOrchestrator:
    """
    Orchestrates the trading bot with Discord notifications.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the orchestrator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.notifier: Optional[DiscordNotifier] = None
        self.bot: Optional[TradingBot] = None
        self._initialize_notifier()
    
    def _initialize_notifier(self):
        """Initialize Discord notifier if enabled."""
        if not self.config.DISCORD_ENABLED:
            print("⚠️  Discord notifications disabled. Set DISCORD_WEBHOOK_URL or DISCORD_BOT_TOKEN.")
            return
        
        try:
            self.notifier = DiscordNotifier(
                webhook_url=self.config.DISCORD_WEBHOOK_URL,
                bot_token=self.config.DISCORD_BOT_TOKEN,
                channel_id=self.config.DISCORD_CHANNEL_ID
            )
            print("✓ Discord notifier initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Discord notifier: {e}")
            self.notifier = None
    
    async def notify_signal(self, signal_type: SignalType, ticker: str, 
                           price: float, confidence: float, 
                           indicators: Optional[dict] = None):
        """Send signal notification to Discord."""
        if not self.notifier:
            return
        
        try:
            await self.notifier.send_signal(
                signal_type=signal_type,
                ticker=ticker,
                price=price,
                confidence=confidence,
                indicators=indicators
            )
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
    
    def notify_signal_sync(self, signal_type: SignalType, ticker: str, 
                          price: float, confidence: float, 
                          indicators: Optional[dict] = None):
        """Synchronous wrapper for notify_signal."""
        if not self.notifier:
            return
        
        try:
            if signal_type == SignalType.BUY:
                self.notifier.send_buy_signal_sync(ticker, price, confidence, indicators)
            elif signal_type == SignalType.SELL:
                self.notifier.send_sell_signal_sync(ticker, price, confidence, indicators)
            else:
                self.notifier.send_signal_sync(signal_type, ticker, price, confidence, 
                                              indicators=indicators)
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
    
    def run_analysis(self, ticker: str, start_date: str, end_date: Optional[str] = None,
                    enable_breakout_filter: bool = True) -> bool:
        """
        Run complete trading analysis with Discord notifications.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today
            enable_breakout_filter: Enable breakout candle filter
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n{'='*70}")
            print(f"TRADING BOT - STARTING ANALYSIS")
            print(f"{'='*70}")
            print(f"Ticker: {ticker}")
            print(f"Date Range: {start_date} to {end_date or 'TODAY'}")
            print(f"Notifications: {'ENABLED' if self.notifier else 'DISABLED'}")
            print(f"{'='*70}\n")
            
            # Create trading bot
            self.bot = TradingBot(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                enable_breakout_filter=enable_breakout_filter,
                verbose=True,
                data_provider=self.config.DATA_PROVIDER
            )
            
            # Step 1: Fetch data
            print("\n[STEP 1] Fetching market data...")
            if not self.bot.fetch_data():
                if self.notifier:
                    self.notifier.send_error_sync(f"Failed to fetch data for {ticker}")
                return False
            
            # Step 2: Convert to Heikin-Ashi
            print("\n[STEP 2] Converting to Heikin-Ashi candles...")
            if not self.bot.convert_to_heikin_ashi():
                if self.notifier:
                    self.notifier.send_error_sync(f"Failed to convert data for {ticker}")
                return False
            
            # Step 3: Calculate signals
            print("\n[STEP 3] Calculating technical indicators and signals...")
            if not self.bot.calculate_signals():
                if self.notifier:
                    self.notifier.send_error_sync(f"Failed to calculate signals for {ticker}")
                return False
            
            # Step 4: Process and send signals
            print("\n[STEP 4] Processing signals and sending notifications...")
            self._process_and_notify_signals()
            
            # Step 5: Summary
            print(f"\n{'='*70}")
            print("✓ ANALYSIS COMPLETE")
            print(f"{'='*70}\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
            if self.notifier:
                self.notifier.send_error_sync(f"Critical error analyzing {ticker}: {str(e)}")
            return False
    
    def _process_and_notify_signals(self):
        """Process signals and send Discord notifications."""
        if self.bot is None or self.bot.signal_data is None:
            print("❌ No signal data available")
            return
        
        # Get latest signal
        latest_signal = self.bot.signal_data.iloc[-1] if len(self.bot.signal_data) > 0 else None
        if latest_signal is None:
            print("❌ No latest signal found")
            return
        
        ticker = self.bot.ticker
        current_price = latest_signal.get('Close', 0)
        signal_type = latest_signal.get('ENTRY_SIGNAL', 0)
        confidence = latest_signal.get('CONFIDENCE_SCORE', 0)
        
        if confidence is None:
            confidence = 0.5
        
        # Normalize confidence to 0-1 range if it's in points
        if confidence > 1:
            confidence = min(confidence / 10.0, 1.0)  # Assume max 10 points
        
        # Collect indicator values
        indicators = {}
        indicator_fields = ['ALLIGATOR_TREND', 'STOCH_RSI', 'VORTEX_SIGNAL', 
                           'BREAKOUT_VALIDATED', 'POINTS']
        for field in indicator_fields:
            if field in latest_signal.index:
                value = latest_signal[field]
                if isinstance(value, float):
                    indicators[field] = f"{value:.2f}"
                else:
                    indicators[field] = str(value)
        
        # Send appropriate notification
        if signal_type == 1:
            print(f"✓ BUY SIGNAL detected for {ticker}")
            if self.notifier:
                self.notifier.send_buy_signal_sync(ticker, current_price, confidence, indicators)
            elif self.config.NOTIFY_ON_BUY:
                print(f"  Price: ${current_price:.2f}")
                print(f"  Confidence: {confidence * 100:.1f}%")
        
        elif signal_type == -1:
            print(f"✓ SELL SIGNAL detected for {ticker}")
            if self.notifier:
                self.notifier.send_sell_signal_sync(ticker, current_price, confidence, indicators)
            elif self.config.NOTIFY_ON_SELL:
                print(f"  Price: ${current_price:.2f}")
                print(f"  Confidence: {confidence * 100:.1f}%")
        
        else:
            print(f"⊙ No trading signal for {ticker} (hold position)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Trading Bot with Discord Notifications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ticker AAPL --start 2024-01-01
  python main.py --ticker TSLA --start 2024-01-01 --end 2024-12-31 --provider yahoo
  python main.py --config analysis_config.json
        """
    )
    
    parser.add_argument('--ticker', type=str, help='Stock ticker symbol (e.g., AAPL, TSLA)')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default=None, help='End date (YYYY-MM-DD)')
    parser.add_argument('--provider', type=str, default='yahoo',
                       choices=['yahoo', 'ibkr', 'alpaca'],
                       help='Data provider (default: yahoo)')
    parser.add_argument('--config', type=str, help='JSON config file')
    parser.add_argument('--no-breakout-filter', action='store_true',
                       help='Disable breakout candle filter')
    parser.add_argument('--check-config', action='store_true',
                       help='Validate configuration and exit')
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config()
    config.print_config()
    
    # Check configuration validity
    if args.check_config:
        is_valid, message = config.validate()
        print(message)
        return 0 if is_valid else 1
    
    # Validate configuration
    is_valid, message = config.validate()
    if not is_valid:
        print(f"⚠️  {message}")
    else:
        print(f"✓ {message}")
    
    # Parse arguments
    if args.config:
        # Load from config file
        try:
            with open(args.config, 'r') as f:
                config_data = json.load(f)
            ticker = config_data.get('ticker')
            start_date = config_data.get('start_date')
            end_date = config_data.get('end_date')
            enable_breakout_filter = config_data.get('enable_breakout_filter', True)
        except Exception as e:
            print(f"❌ Error loading config file: {e}")
            return 1
    else:
        # Parse command line arguments
        if not args.ticker or not args.start:
            parser.print_help()
            return 1
        
        ticker = args.ticker
        start_date = args.start
        end_date = args.end
        enable_breakout_filter = not args.no_breakout_filter
    
    # Create orchestrator and run analysis
    orchestrator = BotOrchestrator(config)
    success = orchestrator.run_analysis(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        enable_breakout_filter=enable_breakout_filter
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
