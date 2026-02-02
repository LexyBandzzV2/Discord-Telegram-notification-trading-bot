
 # TRADING BOT - Main Strategy File
#==================================#
# This file orchestrates the complete trading strategy:
# 1. Fetches stock data from Yahoo Finance
# 2. Converts to Heikin-Ashi candles
# 3. Calculates indicators (Alligator, Stochastic, Vortex)
# 4. Generates buy/sell signals with breakout validation
# 5. Displays trading signals and analysis 

import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from indicators import generate_signals, prepare_ml_features
from data_fetcher import DataFetcher, get_available_providers

# Import Heikin-Ashi converter
import importlib.util
spec = importlib.util.spec_from_file_location("heikin_ashi", 
    os.path.join(os.path.dirname(__file__), "Heikin Ashi.py"))
heikin_ashi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(heikin_ashi)
to_heikin_ashi = heikin_ashi.to_heikin_ashi


class TradingBot:
    """
    Main trading bot class that orchestrates the entire strategy.
    """
    
    def __init__(self, ticker: str, start_date: str, end_date: str = None,
                 enable_breakout_filter: bool = True, verbose: bool = True,
                 data_provider: str = 'yahoo', **provider_kwargs):
        """
        Initialize the trading bot.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'ES')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (default: today)
            enable_breakout_filter: Apply breakout candle validation
            verbose: Print detailed information
            data_provider: Data source ('yahoo', 'ibkr', 'alpaca')
            **provider_kwargs: Additional provider-specific arguments
                - ibkr_host, ibkr_port for Interactive Brokers
                - alpaca_api_key, alpaca_secret_key for Alpaca
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.enable_breakout_filter = enable_breakout_filter
        self.verbose = verbose
        self.data_provider = data_provider
        self.provider_kwargs = provider_kwargs
        
        # Data containers
        self.raw_data = None
        self.ha_data = None
        self.signal_data = None
        
        # Initialize data fetcher
        self.fetcher = DataFetcher(provider=data_provider, **provider_kwargs)
        
    def fetch_data(self):
        """Fetch OHLCV data from selected provider."""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"FETCHING DATA FOR {self.ticker}")
            print(f"{'='*60}")
            print(f"Provider: {self.data_provider.upper()}")
            print(f"Date Range: {self.start_date} to {self.end_date}")
        
        try:
            self.raw_data = self.fetcher.fetch(
                ticker=self.ticker,
                start=self.start_date,
                end=self.end_date
            )
            
            if self.raw_data.empty:
                raise ValueError(f"No data fetched for {self.ticker}. Check ticker symbol and dates.")
            
            if self.verbose:
                print(f"✓ Fetched {len(self.raw_data)} rows of data")
                print(f"  Date range: {self.raw_data.index[0]} to {self.raw_data.index[-1]}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error fetching data: {e}")
            return False
    
    def convert_to_heikin_ashi(self):
        """Convert standard OHLCV to Heikin-Ashi."""
        if self.raw_data is None:
            print("✗ No raw data available. Run fetch_data() first.")
            return False
        
        if self.verbose:
            print(f"\n{'='*60}")
            print("CONVERTING TO HEIKIN-ASHI")
            print(f"{'='*60}")
        
        try:
            self.ha_data = to_heikin_ashi(self.raw_data.copy(), keep_original=True)
            
            if self.verbose:
                print(f"✓ Converted to Heikin-Ashi ({len(self.ha_data)} candles)")
                print(f"  Columns: {list(self.ha_data.columns)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error converting to HA: {e}")
            return False
    
    def calculate_signals(self):
        """Calculate indicators and generate trading signals."""
        if self.ha_data is None:
            print("✗ No Heikin-Ashi data available. Run convert_to_heikin_ashi() first.")
            return False
        
        if self.verbose:
            print(f"\n{'='*60}")
            print("CALCULATING INDICATORS & SIGNALS")
            print(f"{'='*60}")
            print(f"Breakout Filter: {'ENABLED' if self.enable_breakout_filter else 'DISABLED'}")
        
        try:
            self.signal_data = generate_signals(
                self.ha_data.copy(),
                enable_breakout_filter=self.enable_breakout_filter
            )
            
            # Count signals
            buy_signals = (self.signal_data['ENTRY_SIGNAL'] == 1).sum()
            sell_signals = (self.signal_data['ENTRY_SIGNAL'] == -1).sum()
            
            if self.verbose:
                print(f"✓ Indicators calculated successfully")
                print(f"  Total candles analyzed: {len(self.signal_data)}")
                print(f"  Buy signals found: {buy_signals}")
                print(f"  Sell signals found: {sell_signals}")
                print(f"  Total signals: {buy_signals + sell_signals}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error calculating signals: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_signals(self, last_n: int = 10):
        """
        Get the most recent trading signals.
        
        Args:
            last_n: Number of recent signals to return
            
        Returns:
            DataFrame with recent signals
        """
        if self.signal_data is None:
            print("✗ No signal data available. Run calculate_signals() first.")
            return None
        
        # Filter for only rows with signals
        signals = self.signal_data[self.signal_data['ENTRY_SIGNAL'] != 0].copy()
        
        if signals.empty:
            print("ℹ No trading signals found in the analyzed period.")
            return signals
        
        # Select relevant columns
        display_cols = [
            'Open', 'High', 'Low', 'Close', 'Volume',
            'ENTRY_SIGNAL', 'SIGNAL_QUALITY', 'BREAKOUT_RANK',
            'BREAKOUT_REASON', 'STRUCTURE_PATTERN',
            'NEAR_RESISTANCE', 'NEAR_SUPPORT'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in display_cols if col in signals.columns]
        
        return signals[available_cols].tail(last_n)
    
    def display_summary(self):
        """Display a summary of the analysis and signals."""
        if self.signal_data is None:
            print("✗ No signal data available.")
            return
        
        print(f"\n{'='*60}")
        print(f"TRADING SIGNALS SUMMARY - {self.ticker}")
        print(f"{'='*60}")
        
        signals = self.signal_data[self.signal_data['ENTRY_SIGNAL'] != 0]
        
        if signals.empty:
            print("ℹ No trading signals generated in this period.")
            print("\nPossible reasons:")
            print("  • Indicators not aligned (all 3 must confirm)")
            print("  • Breakout filter rejected candles (dojis, weak candles)")
            print("  • Alligator 'mouth' not open (consolidating market)")
            print("\nTry:")
            print("  • Extending the date range")
            print("  • Disabling breakout filter (enable_breakout_filter=False)")
            print("  • Checking a more volatile stock")
            return
        
        # Signal breakdown
        buy_signals = signals[signals['ENTRY_SIGNAL'] == 1]
        sell_signals = signals[signals['ENTRY_SIGNAL'] == -1]
        
        print(f"\n📊 SIGNAL BREAKDOWN:")
        print(f"  BUY signals:  {len(buy_signals)}")
        print(f"  SELL signals: {len(sell_signals)}")
        print(f"  Total:        {len(signals)}")
        
        # Signal quality
        if 'SIGNAL_QUALITY' in signals.columns:
            avg_quality = signals['SIGNAL_QUALITY'].mean()
            print(f"\n⭐ AVERAGE SIGNAL QUALITY: {avg_quality:.2%}")
        
        # Most recent signals
        print(f"\n📈 MOST RECENT SIGNALS (Last 5):")
        print("-" * 60)
        
        recent = signals.tail(5)
        for idx, row in recent.iterrows():
            signal_type = "🟢 BUY" if row['ENTRY_SIGNAL'] == 1 else "🔴 SELL"
            date_str = idx.strftime('%Y-%m-%d %H:%M') if hasattr(idx, 'strftime') else str(idx)
            
            print(f"\n{signal_type} @ {date_str}")
            print(f"  Price: ${row['Close']:.2f}")
            
            if 'SIGNAL_QUALITY' in row:
                print(f"  Quality: {row['SIGNAL_QUALITY']:.1%}")
            
            if 'BREAKOUT_RANK' in row and row['BREAKOUT_RANK'] > 0:
                print(f"  Breakout Rank: #{int(row['BREAKOUT_RANK'])} of 3")
            
            if 'STRUCTURE_PATTERN' in row and row['STRUCTURE_PATTERN']:
                print(f"  Pattern: {row['STRUCTURE_PATTERN']}")
        
        print(f"\n{'='*60}\n")
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline."""
        print(f"\n{'#'*60}")
        print(f"# TRADING BOT - FULL ANALYSIS")
        print(f"# Ticker: {self.ticker}")
        print(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}")
        
        # Step 1: Fetch data
        if not self.fetch_data():
            return False
        
        # Step 2: Convert to Heikin-Ashi
        if not self.convert_to_heikin_ashi():
            return False
        
        # Step 3: Calculate signals
        if not self.calculate_signals():
            return False
        
        # Step 4: Display results
        self.display_summary()
        
        return True
    
    def export_signals(self, filename: str = None):
        """
        Export signals to CSV file.
        
        Args:
            filename: Output filename (default: ticker_signals_YYYYMMDD.csv)
        """
        if self.signal_data is None:
            print("✗ No signal data to export.")
            return False
        
        if filename is None:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{self.ticker}_signals_{date_str}.csv"
        
        # Only export rows with signals
        signals = self.signal_data[self.signal_data['ENTRY_SIGNAL'] != 0]
        
        try:
            signals.to_csv(filename)
            print(f"✓ Signals exported to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Error exporting signals: {e}")
            return False


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Example usage of the trading bot.
    Modify the parameters below to customize your analysis.
    """
    
    # -------------------------------------------------------------------------
    # CONFIGURATION - MULTI-PROVIDER DATA SOURCE
    # -------------------------------------------------------------------------
    
    # Display available providers
    print("\n" + "="*60)
    print("AVAILABLE DATA PROVIDERS")
    print("="*60)
    providers = get_available_providers()
    for name, available in providers.items():
        status = "✓ Ready" if available else "✗ Not installed"
        print(f"  {name.upper():<10} {status}")
    print("="*60 + "\n")
    
    # -------------------------------------------------------------------------
    # DATA PROVIDER CONFIGURATION
    # -------------------------------------------------------------------------
    
    # OPTION 1: Yahoo Finance (Free, No setup required)
    DATA_PROVIDER = 'yahoo'
    PROVIDER_CONFIG = {}
    
    # OPTION 2: Interactive Brokers (Real futures, requires TWS/Gateway running)
    # DATA_PROVIDER = 'ibkr'
    # PROVIDER_CONFIG = {
    #     'ibkr_host': '127.0.0.1',
    #     'ibkr_port': 7497,  # 7497=paper trading, 7496=live trading
    # }
    
    # OPTION 3: Alpaca (Stocks & Crypto, requires API keys)
    # DATA_PROVIDER = 'alpaca'
    # PROVIDER_CONFIG = {
    #     'alpaca_api_key': 'YOUR_API_KEY_HERE',
    #     'alpaca_secret_key': 'YOUR_SECRET_KEY_HERE'
    # }
    
    # -------------------------------------------------------------------------
    # TICKER CONFIGURATION
    # -------------------------------------------------------------------------
    
    # YAHOO FINANCE OPTIONS:
    TICKER = "TSLA"              # Tesla (very volatile)
    # TICKER = "ES=F"            # S&P 500 E-mini Futures (delayed)
    # TICKER = "NQ=F"            # NASDAQ-100 E-mini Futures (delayed)
    # TICKER = "SPY"             # S&P 500 ETF
    # TICKER = "QQQ"             # NASDAQ-100 ETF
    # TICKER = "GME"             # GameStop (extremely volatile)
    
    # INTERACTIVE BROKERS OPTIONS (use symbol only, not with =F):
    # TICKER = "ES"              # S&P 500 E-mini Futures (real-time)
    # TICKER = "NQ"              # NASDAQ-100 E-mini Futures (real-time)
    # TICKER = "YM"              # Dow Jones E-mini Futures (real-time)
    # TICKER = "CL"              # Crude Oil Futures
    # TICKER = "GC"              # Gold Futures
    
    # ALPACA OPTIONS:
    # TICKER = "AAPL"            # Apple stock
    # TICKER = "BTCUSD"          # Bitcoin futures
    
    START_DATE = "2024-01-01"    # Analysis start date
    END_DATE = None               # Analysis end date (None = today)
    ENABLE_BREAKOUT_FILTER = False # Disable for more signals initially
    
    # -------------------------------------------------------------------------
    # RUN ANALYSIS
    # -------------------------------------------------------------------------
    
    # Create bot instance
    bot = TradingBot(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
        enable_breakout_filter=ENABLE_BREAKOUT_FILTER,
        data_provider=DATA_PROVIDER,
        verbose=True,
        **PROVIDER_CONFIG
    )
    
    # Run full analysis
    success = bot.run_full_analysis()
    
    if success:
        # Get detailed signal data
        signals = bot.get_signals(last_n=10)
        
        if signals is not None and not signals.empty:
            print("\n📋 DETAILED SIGNAL DATA:")
            print("="*60)
            print(signals.to_string())
            
            # Optional: Export to CSV
            # bot.export_signals()
        
        print("\n✓ Analysis complete!")
    else:
        print("\n✗ Analysis failed. Check errors above.")
    
    # -------------------------------------------------------------------------
    # QUICK ACCESS TO DATA
    # -------------------------------------------------------------------------
    # After running, you can access:
    # - bot.raw_data        : Original OHLCV data
    # - bot.ha_data         : Heikin-Ashi converted data
    # - bot.signal_data     : Full data with all indicators and signals
    # - bot.get_signals()   : Filtered view of just the signals
