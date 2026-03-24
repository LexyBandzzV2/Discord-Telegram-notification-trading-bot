"""
Configuration Module
====================
Centralized configuration for all trading bot settings.
Multi-timeframe trading with Discord notifications.

Environment Variables:
  DISCORD_BOT_TOKEN      - Discord bot token
  GOOGLE_API_KEY         - Google Gemini API key for LLM features
  IBKR_HOST              - Interactive Brokers host
  IBKR_PORT              - Interactive Brokers port
  IBKR_CLIENT_ID         - Interactive Brokers client ID
  ALPACA_API_KEY         - Alpaca API key
  ALPACA_SECRET_KEY      - Alpaca secret key
  DATA_PROVIDER          - Default data provider (yahoo, ibkr, alpaca)
  DEBUG                  - Enable debug logging (true/false)
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Base configuration class."""
    
    # ==================== DISCORD CONFIGURATION ====================
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
    DISCORD_ENABLED = bool(DISCORD_BOT_TOKEN)
    
    # Timeframe-specific channel IDs for multi-timeframe analysis
    DISCORD_CHANNELS = {
        '1m': os.getenv('DISCORD_CHANNEL_1M', '1469430219965202503'),
        '5m': os.getenv('DISCORD_CHANNEL_5M', '1469430267981729823'),
        '15m': os.getenv('DISCORD_CHANNEL_15M', '1469430293806186743'),
        '1h': os.getenv('DISCORD_CHANNEL_1H', '1469430391512502438'),
    }
    
    # Bot commands channel (for !analyze commands and responses)
    DISCORD_COMMANDS_CHANNEL = os.getenv('DISCORD_COMMANDS_CHANNEL', '1469452751871279196')
    
    # Asset-specific Discord channel IDs
    ASSET_CHANNELS = {
        'BTC-USD': '1469824428094390476',
        'ETH-USD': '1469824450043187241',
        'XRP-USD': '1469824806210895975',
        'SLV': '1469824831687229691',
        'GLD': '1469824849047453833',
        'AAPL': '1469824524982685759',
        'TSLA': '1469824559602471107',
        'NVDA': '1469824493357629784',
        '^GSPC': '1469824916298928514',
    }
    
    # Special channels
    DAILY_NEWS_CHANNEL = '1469829203280138433'
    DAILY_SUMMARY_CHANNEL = '1469829254756831263'
    
    # ==================== LLM CONFIGURATION ====================
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
    LLM_ENABLED = bool(os.getenv('GOOGLE_API_KEY', ''))
    
    # ==================== TRADING CONFIGURATION ====================
    # Primary tickers to monitor
    PRIMARY_TICKERS = ['TSLA', 'BTC-USD', 'AAPL', 'ETH-USD', '^GSPC', 'XRP-USD', 'NVDA', 'GLD', 'SLV']
    
    # Timeframes to analyze (in minutes)
    TIMEFRAMES = ['1m', '5m', '15m', '1h']
    
    # Ticker display names for Discord messages
    TICKER_NAMES = {
        'TSLA': '🚗 Tesla',
        'BTC-USD': '₿ Bitcoin',
        'AAPL': '🍎 Apple',
        'ETH-USD': 'Ξ Ethereum',
        '^GSPC': '📈 S&P 500',
        'XRP-USD': '💧 XRP',
        'NVDA': '🔧 NVIDIA',
        'GLD': '🥇 Gold',
        'SLV': '⚪ Silver',
    }
    
    # Data Provider Configuration
    DATA_PROVIDER = os.getenv('DATA_PROVIDER', 'yahoo')
    IBKR_HOST = os.getenv('IBKR_HOST', '127.0.0.1')
    IBKR_PORT = int(os.getenv('IBKR_PORT', '7497'))
    IBKR_CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', '1'))
    
    # Alpaca Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # TradingView Configuration
    TRADINGVIEW_USERNAME = os.getenv('TRADINGVIEW_USERNAME', '')
    TRADINGVIEW_PASSWORD = os.getenv('TRADINGVIEW_PASSWORD', '')
    
    # ==================== BOT CONFIGURATION ====================
    DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']
    DEFAULT_LOOKBACK_DAYS = 365
    DEFAULT_INTERVAL = '1d'
    ENABLE_BREAKOUT_FILTER = True
    
    # ==================== SIGNAL CONFIGURATION ====================
    MIN_CONFIDENCE_THRESHOLD = 0.6
    MIN_POINTS_FOR_SIGNAL = 3
    
    # ==================== NOTIFICATION CONFIGURATION ====================
    NOTIFY_ON_BUY = True
    NOTIFY_ON_SELL = True
    NOTIFY_ON_ERROR = True
    NOTIFY_ON_ALERT = True
    
    # ==================== TIMEFRAME SETTINGS ====================
    # Lookback periods for different timeframes (in days)
    TIMEFRAME_LOOKBACK = {
        '1m': 7,      # 7 days for 1-minute bars
        '5m': 7,      # 7 days for 5-minute bars
        '15m': 14,    # 14 days for 15-minute bars
        '1h': 60,     # 60 days for hourly bars
    }
    
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """
        Validate critical configuration settings.
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not cls.DISCORD_ENABLED:
            return False, "❌ Discord bot not configured. Set DISCORD_BOT_TOKEN environment variable."
        
        if not all(cls.DISCORD_CHANNELS.values()):
            return False, "❌ Not all Discord channel IDs are configured."
        
        if cls.DATA_PROVIDER == 'ibkr' and not cls.IBKR_HOST:
            return False, "❌ Data provider set to 'ibkr' but IBKR_HOST not configured."
        
        if cls.DATA_PROVIDER == 'alpaca' and not cls.ALPACA_API_KEY:
            return False, "❌ Data provider set to 'alpaca' but ALPACA_API_KEY not configured."
        
        return True, "✓ Configuration validated successfully"
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)."""
        print("\n" + "=" * 70)
        print("🤖 TRADING BOT CONFIGURATION")
        print("=" * 70)
        print(f"✓ Discord Enabled: {cls.DISCORD_ENABLED}")
        print(f"✓ Data Provider: {cls.DATA_PROVIDER}")
        print(f"✓ Debug Mode: {cls.DEBUG}")
        print(f"\n📊 Tickers to Monitor: {', '.join(cls.PRIMARY_TICKERS)}")
        print(f"⏱️  Timeframes: {', '.join(cls.TIMEFRAMES)}")
        print(f"\n🎯 Signal Thresholds:")
        print(f"   Min Confidence: {cls.MIN_CONFIDENCE_THRESHOLD * 100:.0f}%")
        print(f"   Min Points: {cls.MIN_POINTS_FOR_SIGNAL}")
        print(f"\n📢 Discord Channels:")
        for tf, channel_id in cls.DISCORD_CHANNELS.items():
            print(f"   {tf}: {channel_id}")
        print("=" * 70 + "\n")
    
    @classmethod
    def get_channel_for_timeframe(cls, timeframe: str) -> str:
        """Get Discord channel ID for a specific timeframe."""
        return cls.DISCORD_CHANNELS.get(timeframe, cls.DISCORD_CHANNELS['1h'])
    
    @classmethod
    def get_channel_for_asset(cls, ticker: str) -> str:
        """Get Discord channel ID for a specific asset."""
        return cls.ASSET_CHANNELS.get(ticker, '')
    
    @classmethod
    def get_ticker_display_name(cls, ticker: str) -> str:
        """Get display name for a ticker."""
        return cls.TICKER_NAMES.get(ticker, ticker)
    
    @classmethod
    def get_discord_config(cls) -> Optional[dict]:
        """Get Discord configuration as dictionary."""
        if not cls.DISCORD_ENABLED:
            return None
        
        return {
            'bot_token': cls.DISCORD_BOT_TOKEN,
            'channels': cls.DISCORD_CHANNELS
        }
    
    @classmethod
    def get_discord_config(cls) -> Optional[dict]:
        """Get Discord configuration as dictionary."""
        if not cls.DISCORD_ENABLED:
            return None
        
        return {
            'webhook_url': cls.DISCORD_WEBHOOK_URL,
            'bot_token': cls.DISCORD_BOT_TOKEN,
            'channel_id': cls.DISCORD_CHANNEL_ID
        }
    
    @classmethod
    def get_data_provider_config(cls) -> dict:
        """Get data provider configuration as dictionary."""
        config = {'provider': cls.DATA_PROVIDER}
        
        if cls.DATA_PROVIDER == 'ibkr':
            config.update({
                'ibkr_host': cls.IBKR_HOST,
                'ibkr_port': cls.IBKR_PORT,
                'ibkr_client_id': cls.IBKR_CLIENT_ID,
            })
        elif cls.DATA_PROVIDER == 'alpaca':
            config.update({
                'alpaca_api_key': cls.ALPACA_API_KEY,
                'alpaca_secret_key': cls.ALPACA_SECRET_KEY,
                'alpaca_base_url': cls.ALPACA_BASE_URL,
            })
        
        return config


class DevelopmentConfig(Config):
    """Development configuration (with debug mode enabled)."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration (debug disabled)."""
    DEBUG = False


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
