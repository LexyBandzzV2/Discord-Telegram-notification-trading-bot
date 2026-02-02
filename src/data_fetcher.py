"""
Multi-Provider Data Fetcher
============================
Supports multiple data sources:
- Yahoo Finance (stocks, ETFs, delayed futures)
- Interactive Brokers (real-time futures, stocks, options)
- Alpaca (stocks, crypto futures)

Usage:
    fetcher = DataFetcher(provider='yahoo')  # or 'ibkr' or 'alpaca'
    data = fetcher.fetch(ticker='ES=F', start='2024-01-01')
"""

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Literal

# Provider imports (will install as needed)
IBKR_AVAILABLE = False
ALPACA_AVAILABLE = False
TRADINGVIEW_AVAILABLE = False

try:
    from ib_insync import IB, Future, Stock, util
    IBKR_AVAILABLE = True
except ImportError:
    pass

try:
    from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
    from alpaca.data.timeframe import TimeFrame
    ALPACA_AVAILABLE = True
except ImportError:
    pass

try:
    from tvDatafeed import TvDatafeed, Interval
    TRADINGVIEW_AVAILABLE = True
except ImportError:
    pass


class DataFetcher:
    """
    Universal data fetcher supporting multiple providers.
    """
    
    def __init__(self, provider: Literal['yahoo', 'ibkr', 'alpaca', 'tradingview'] = 'yahoo',
                 ibkr_host: str = None, ibkr_port: int = None, ibkr_client_id: int = None,
                 alpaca_api_key: str = None, alpaca_secret_key: str = None,
                 alpaca_base_url: str = None):
        """
        Initialize the data fetcher.
        
        Args:
            provider: Data provider ('yahoo', 'ibkr', 'alpaca', 'tradingview')
            ibkr_host: Interactive Brokers TWS/Gateway host
            ibkr_port: Interactive Brokers TWS/Gateway port (7497=paper, 7496=live)
            ibkr_client_id: Client ID for IBKR connection (default: 1)
            alpaca_api_key: Alpaca API key
            alpaca_secret_key: Alpaca secret key
            alpaca_base_url: Alpaca API base URL
        """
        self.provider = provider
        
        # Load from environment variables if not provided
        self.ibkr_host = ibkr_host or os.getenv('IBKR_HOST', '127.0.0.1')
        self.ibkr_port = ibkr_port or int(os.getenv('IBKR_PORT', '7497'))
        self.ibkr_client_id = ibkr_client_id or int(os.getenv('IBKR_CLIENT_ID', '1'))
        self.alpaca_api_key = alpaca_api_key or os.getenv('ALPACA_API_KEY')
        self.alpaca_secret_key = alpaca_secret_key or os.getenv('ALPACA_SECRET_KEY')
        self.alpaca_base_url = alpaca_base_url or os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        # Connection objects
        self.ib = None
        self.alpaca_stock_client = None
        self.alpaca_crypto_client = None
        self.tv = None
        
    def fetch(self, ticker: str, start: str, end: str = None,
              interval: str = '1d', contract_month: str = None) -> pd.DataFrame:
        """
        Fetch OHLCV data from the selected provider.
        
        Args:
            ticker: Symbol (e.g., 'AAPL', 'ES', 'BTCUSD')
            start: Start date 'YYYY-MM-DD'
            end: End date 'YYYY-MM-DD' (default: today)
            interval: Timeframe ('1m', '5m', '15m', '1h', '1d')
            contract_month: For futures - contract month (e.g., '202503' for March 2025)
            
        Returns:
            DataFrame with OHLCV data
        """
        if self.provider == 'yahoo':
            return self._fetch_yahoo(ticker, start, end, interval)
        elif self.provider == 'ibkr':
            return self._fetch_ibkr(ticker, start, end, interval, contract_month)
        elif self.provider == 'alpaca':
            return self._fetch_alpaca(ticker, start, end, interval)
        elif self.provider == 'tradingview':
            return self._fetch_tradingview(ticker, start, end, interval)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    # =========================================================================
    # YAHOO FINANCE
    # =========================================================================
    
    def _fetch_yahoo(self, ticker: str, start: str, end: str = None,
                     interval: str = '1d') -> pd.DataFrame:
        """Fetch data from Yahoo Finance."""
        end = end or datetime.now().strftime('%Y-%m-%d')
        
        # Map intervals to yfinance format
        interval_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '1d': '1d', '1wk': '1wk', '1mo': '1mo'
        }
        yf_interval = interval_map.get(interval, '1d')
        
        data = yf.download(ticker, start=start, end=end, interval=yf_interval,
                          progress=False, auto_adjust=True)
        
        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        return data
    
    # =========================================================================
    # INTERACTIVE BROKERS
    # =========================================================================
    
    def _fetch_ibkr(self, ticker: str, start: str, end: str = None,
                    interval: str = '1d', contract_month: str = None) -> pd.DataFrame:
        """Fetch data from Interactive Brokers."""
        if not IBKR_AVAILABLE:
            raise ImportError(
                "ib_insync not installed. Install with: pip install ib_insync"
            )
        
        # Connect to TWS/Gateway
        if self.ib is None:
            self.ib = IB()
            try:
                self.ib.connect(self.ibkr_host, self.ibkr_port, clientId=self.ibkr_client_id)
                print(f"✓ Connected to Interactive Brokers on {self.ibkr_host}:{self.ibkr_port} (Client ID: {self.ibkr_client_id})")
            except Exception as e:
                raise ConnectionError(
                    f"Failed to connect to Interactive Brokers. "
                    f"Make sure TWS/Gateway is running on port {self.ibkr_port}. "
                    f"Error: {e}"
                )
        elif not self.ib.isConnected():
            # Reconnect if disconnected
            try:
                self.ib.connect(self.ibkr_host, self.ibkr_port, clientId=self.ibkr_client_id)
                print(f"✓ Reconnected to Interactive Brokers")
            except Exception as e:
                raise ConnectionError(f"Failed to reconnect to Interactive Brokers: {e}")
        
        # Determine contract type
        if ticker in ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'NG', 'ZB', 'ZN']:
            # Futures contract
            contract_month = contract_month or self._get_front_month()
            # Determine exchange based on product
            exchange = 'NYMEX' if ticker in ['CL', 'NG'] else 'GLOBEX'
            contract = Future(ticker, contract_month, exchange)
        else:
            # Stock
            contract = Stock(ticker, 'SMART', 'USD')
        
        # Qualify contract
        qualified = self.ib.qualifyContracts(contract)
        if not qualified:
            raise ValueError(f"Could not qualify contract for ticker: {ticker}")
        contract = qualified[0]
        
        # Map interval to IB format
        bar_size_map = {
            '1m': '1 min', '5m': '5 mins', '15m': '15 mins', '30m': '30 mins',
            '1h': '1 hour', '1d': '1 day', '1wk': '1 week', '1mo': '1 month'
        }
        bar_size = bar_size_map.get(interval, '1 day')
        
        # Calculate duration
        start_dt = datetime.strptime(start, '%Y-%m-%d')
        end_dt = datetime.strptime(end, '%Y-%m-%d') if end else datetime.now()
        duration_days = (end_dt - start_dt).days
        
        if duration_days > 365:
            duration = f"{duration_days // 365} Y"
        else:
            duration = f"{duration_days} D"
        
        # Fetch bars
        try:
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=False,  # Include extended hours
                formatDate=1
            )
        except Exception as e:
            raise RuntimeError(f"Failed to fetch IBKR historical data: {e}")
        
        if not bars:
            raise ValueError(f"No data returned for {ticker}")
        
        # Convert to DataFrame
        df = util.df(bars)
        if df.empty:
            raise ValueError(f"Empty DataFrame returned for {ticker}")
        
        df = df.rename(columns={
            'date': 'Date', 'open': 'Open', 'high': 'High',
            'low': 'Low', 'close': 'Close', 'volume': 'Volume'
        })
        df = df.set_index('Date')
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        return df
    
    def _get_front_month(self) -> str:
        """Get the front month contract (current or next month)."""
        now = datetime.now()
        # Futures typically roll mid-month
        if now.day > 15:
            contract_month = (now + timedelta(days=30)).strftime('%Y%m')
        else:
            contract_month = now.strftime('%Y%m')
        return contract_month
    
    # =========================================================================
    # ALPACA
    # =========================================================================
    
    def _fetch_alpaca(self, ticker: str, start: str, end: str = None,
                      interval: str = '1d') -> pd.DataFrame:
        """Fetch data from Alpaca."""
        if not ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-py not installed. Install with: pip install alpaca-py"
            )
        
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            raise ValueError("Alpaca API key and secret key required")
        
        end = end or datetime.now().strftime('%Y-%m-%d')
        
        # Determine if crypto or stock
        is_crypto = any(ticker.endswith(x) for x in ['USD', 'USDT']) or '/' in ticker
        
        # Initialize client
        if is_crypto:
            if self.alpaca_crypto_client is None:
                self.alpaca_crypto_client = CryptoHistoricalDataClient(
                    api_key=self.alpaca_api_key,
                    secret_key=self.alpaca_secret_key
                )
        else:
            if self.alpaca_stock_client is None:
                self.alpaca_stock_client = StockHistoricalDataClient(
                    api_key=self.alpaca_api_key,
                    secret_key=self.alpaca_secret_key
                )
        
        # Map interval to Alpaca TimeFrame
        timeframe_map = {
            '1m': TimeFrame.Minute, '5m': TimeFrame(5, 'Minute'),
            '15m': TimeFrame(15, 'Minute'), '30m': TimeFrame(30, 'Minute'),
            '1h': TimeFrame.Hour, '1d': TimeFrame.Day
        }
        timeframe = timeframe_map.get(interval, TimeFrame.Day)
        
        # Create request
        try:
            if is_crypto:
                request = CryptoBarsRequest(
                    symbol_or_symbols=ticker,
                    timeframe=timeframe,
                    start=start,
                    end=end
                )
                bars = self.alpaca_crypto_client.get_crypto_bars(request)
            else:
                request = StockBarsRequest(
                    symbol_or_symbols=ticker,
                    timeframe=timeframe,
                    start=start,
                    end=end
                )
                bars = self.alpaca_stock_client.get_stock_bars(request)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Alpaca data: {e}")
        
        # Convert to DataFrame
        df = bars.df
        if df.empty:
            raise ValueError(f"No data returned for {ticker} from Alpaca")
        
        df = df.reset_index()
        
        # Handle multi-index (symbol level)
        if 'symbol' in df.columns:
            df = df[df['symbol'] == ticker]
            df = df.drop(columns=['symbol'])
        
        df = df.rename(columns={
            'timestamp': 'Date', 'open': 'Open', 'high': 'High',
            'low': 'Low', 'close': 'Close', 'volume': 'Volume'
        })
        df = df.set_index('Date')
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Ensure timezone-naive index for consistency
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        return df
    
    # =========================================================================
    # TRADINGVIEW
    # =========================================================================
    
    def _fetch_tradingview(self, ticker: str, start: str, end: str = None,
                          interval: str = '1d') -> pd.DataFrame:
        """Fetch real-time data from TradingView."""
        if not TRADINGVIEW_AVAILABLE:
            raise ImportError(
                "tvDatafeed not installed. Install with: pip install tvdatafeed"
            )
        
        # Initialize TvDatafeed connection
        if self.tv is None:
            try:
                self.tv = TvDatafeed()
                print(f"✓ Connected to TradingView")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to TradingView: {e}")
        
        # Map interval to TradingView format
        interval_map = {
            '1m': Interval.in_1_minute,
            '5m': Interval.in_5_minute,
            '15m': Interval.in_15_minute,
            '30m': Interval.in_30_minute,
            '1h': Interval.in_1_hour,
            '1d': Interval.in_daily,
            '1wk': Interval.in_weekly,
            '1mo': Interval.in_monthly
        }
        tv_interval = interval_map.get(interval, Interval.in_daily)
        
        # Determine symbol and symbol type
        # TradingView uses specific format: ticker or ticker@exchange
        symbol = ticker
        
        # Common exchanges for different asset types
        if ticker in ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'NG', 'ZB', 'ZN']:
            # US Futures - use CBOT/NYMEX/CME exchanges
            if ticker in ['ES', 'NQ', 'YM', 'RTY']:
                symbol = f"{ticker}1!"  # CME contract
            elif ticker in ['CL', 'NG']:
                symbol = f"{ticker}1!"  # NYMEX contract
            elif ticker in ['GC', 'ZB', 'ZN']:
                symbol = f"{ticker}1!"  # CBOT contract
        elif '/' in ticker:
            # Crypto pair (e.g., BTCUSD, ETHUSD)
            symbol = ticker.replace('/', '')
        
        try:
            # Fetch historical data
            bars = self.tv.get_hist(
                symbol=symbol,
                interval=tv_interval,
                n_bars=500  # Get enough bars to cover date range
            )
            
            if bars is None or bars.empty:
                raise ValueError(f"No data returned for {ticker} from TradingView")
            
            # Filter by date range
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end) if end else pd.Timestamp.now()
            
            # TradingView returns data with 'time' as index
            if 'time' in bars.columns:
                bars['time'] = pd.to_datetime(bars['time'])
                bars = bars.set_index('time')
            
            # Filter date range
            bars = bars[(bars.index >= start_dt) & (bars.index <= end_dt)]
            
            if bars.empty:
                raise ValueError(f"No data in date range for {ticker}")
            
            # Standardize column names
            bars = bars.rename(columns={
                'open': 'Open', 'high': 'High',
                'low': 'Low', 'close': 'Close', 'volume': 'Volume'
            })
            
            # Keep only required columns
            bars = bars[['Open', 'High', 'Low', 'Close', 'Volume']]
            bars.index.name = 'Date'
            
            return bars
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch TradingView data for {ticker}: {e}")
    
    def disconnect(self):
        """Disconnect from all providers."""
        if self.ib is not None and self.ib.isConnected():
            try:
                self.ib.disconnect()
                print("✓ Disconnected from Interactive Brokers")
            except Exception as e:
                print(f"⚠ Error disconnecting from IBKR: {e}")
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.disconnect()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_available_providers() -> dict:
    """
    Check which providers are available.
    
    Returns:
        Dict with provider availability status
    """
    return {
        'yahoo': True,  # Always available (using yfinance)
        'ibkr': IBKR_AVAILABLE,
        'alpaca': ALPACA_AVAILABLE,
        'tradingview': TRADINGVIEW_AVAILABLE
    }


def install_provider(provider: str):
    """
    Show installation instructions for a provider.
    
    Args:
        provider: Provider name ('ibkr', 'alpaca', or 'tradingview')
    """
    instructions = {
        'ibkr': """
        To install Interactive Brokers support:
        
        1. Install ib_insync:
           pip install ib_insync
        
        2. Download TWS or IB Gateway:
           https://www.interactivebrokers.com/en/trading/tws.php
        
        3. Configure API access:
           - Open TWS/Gateway
           - Go to File > Global Configuration > API > Settings
           - Enable "ActiveX and Socket Clients"
           - Set Socket port: 7497 (paper) or 7496 (live)
           - Add 127.0.0.1 to trusted IPs
        
        4. Usage:
           fetcher = DataFetcher(provider='ibkr', ibkr_port=7497)
           data = fetcher.fetch('ES', '2024-01-01', contract_month='202503')
        """,
        'alpaca': """
        To install Alpaca support:
        
        1. Install alpaca-py:
           pip install alpaca-py
        
        2. Get API keys:
           - Sign up at https://alpaca.markets/
           - Go to Paper Trading account
           - Generate API key and secret
        
        3. Usage:
           fetcher = DataFetcher(
               provider='alpaca',
               alpaca_api_key='YOUR_KEY',
               alpaca_secret_key='YOUR_SECRET'
           )
           data = fetcher.fetch('AAPL', '2024-01-01')
        """,
        'tradingview': """
        To install TradingView support:
        
        1. Install tvDatafeed:
           pip install tvdatafeed
        
        2. No API keys needed - TradingView is free!
        
        3. Usage (Real-time data):
           fetcher = DataFetcher(provider='tradingview')
           data = fetcher.fetch('ES', '2024-01-01')       # S&P 500 futures
           data = fetcher.fetch('BTCUSD', '2024-01-01')   # Bitcoin
           data = fetcher.fetch('AAPL', '2024-01-01')     # Apple stock
        
        4. Supported assets:
           - US Futures: ES, NQ, YM, RTY, CL, GC, NG, ZB, ZN
           - Crypto: BTCUSD, ETHUSD, etc.
           - Stocks: AAPL, TSLA, etc.
        """
    }
    
    print(instructions.get(provider, f"Unknown provider: {provider}"))


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Multi-Provider Data Fetcher")
    print("=" * 60)
    
    # Check available providers
    providers = get_available_providers()
    print("\n📊 Available Providers:")
    for name, available in providers.items():
        status = "✓ Available" if available else "✗ Not installed"
        print(f"  {name.upper():<15} {status}")
    
    # Show installation instructions for missing providers
    if not providers['ibkr']:
        print("\n" + "="*60)
        install_provider('ibkr')
    
    if not providers['alpaca']:
        print("\n" + "="*60)
        install_provider('alpaca')
    
    if not providers['tradingview']:
        print("\n" + "="*60)
        install_provider('tradingview')
    
    # Example: Fetch data from Yahoo Finance
    print("\n" + "="*60)
    print("Example: Fetching TSLA data from Yahoo Finance...")
    print("="*60)
    
    fetcher = DataFetcher(provider='yahoo')
    data = fetcher.fetch('TSLA', start='2024-11-01', end='2024-12-01')
    
    print(f"\n✓ Fetched {len(data)} rows")
    print("\nLast 5 rows:")
    print(data.tail())

    # Yahoo Finance (always works)
    fetcher = DataFetcher(provider='yahoo')
    data = fetcher.fetch('TSLA', '2024-01-01')

    # Alpaca (reads from .env)
    fetcher = DataFetcher(provider='alpaca')
    data = fetcher.fetch('BTC/USD', '2024-01-01')  # Crypto
    data = fetcher.fetch('AAPL', '2024-01-01')     # Stocks

    # Interactive Brokers (reads from .env)
    fetcher = DataFetcher(provider='ibkr')
    data = fetcher.fetch('ES', '2024-01-01')       # Futures
    
    # TradingView (real-time, no API keys needed!)
    fetcher = DataFetcher(provider='tradingview')
    data = fetcher.fetch('ES', '2024-01-01')       # S&P 500 futures (real-time!)
    data = fetcher.fetch('BTCUSD', '2024-01-01')   # Bitcoin (real-time!)
    data = fetcher.fetch('AAPL', '2024-01-01')     # Apple stock (real-time!)

    # Real-time ES (S&P 500 Futures)
    fetcher = DataFetcher(provider='tradingview')
    data = fetcher.fetch('ES', '2024-12-01', '2024-12-13', interval='1d')

    # Bitcoin
    data = fetcher.fetch('BTCUSD', '2024-12-01', '2024-12-13', interval='1h')

    # NASDAQ Futures
    data = fetcher.fetch('NQ', '2024-12-01', '2024-12-13', interval='5m')
