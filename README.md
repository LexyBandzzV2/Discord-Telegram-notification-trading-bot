# Discord/Telegram Notification Trading Bot

A sophisticated automated trading bot that analyzes multiple technical indicators and sends real-time trade notifications to Discord and Telegram. This bot combines advanced charting patterns (Heikin Ashi), multiple technical indicators, and intelligent signal processing to identify high-probability trading opportunities.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Integrations](#api-integrations)
- [Technical Indicators](#technical-indicators)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Multi-Indicator Analysis**: Combines multiple technical indicators to generate robust trading signals
- **Heikin Ashi Candles**: Advanced Japanese candlestick pattern analysis for trend identification
- **Real-Time Notifications**: Sends alerts to Discord and Telegram instantly when trading opportunities are detected
- **N8N Workflow Integration**: Seamlessly integrates with N8N for advanced workflow automation
- **Live Market Data**: Fetches real-time data from TradingView API
- **Strategy Backtesting**: Test trading strategies with historical data before deploying
- **Points System**: Custom scoring system to rate the quality and confidence of trading signals
- **Performance Analysis**: Track successful and unsuccessful trades for continuous improvement

## 📁 Project Structure

```
Discord-Telegram-notification-trading-bot/
├── src/
│   ├── Trading Bot Brain. regular.py    # Main bot logic and orchestration
│   ├── strategy.py                      # Trading strategy implementation
│   ├── indicators.py                    # Technical indicators library
│   ├── Heikin Ashi.py                   # Heikin Ashi candlestick analysis
│   ├── data_fetcher.py                  # Live market data fetching
│   ├── n8n_api.py                       # N8N webhook integration
│   ├── close knit.py                    # Support utilities
│   └── test_multiple.py                 # Testing suite
├── workflows/
│   ├── n8n_trading_workflow.json        # N8N workflow configuration
│   └── n8n.js                           # N8N JavaScript utilities
├── config/                              # Configuration files
├── requirements.txt                     # Python dependencies
├── test_tradingview.py                  # TradingView API tests
└── README.md                            # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Discord Bot Token (optional, for Discord notifications)
- Telegram Bot Token (optional, for Telegram notifications)
- TradingView Account/API access

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/LexyBandzzV2/Discord-Telegram-notification-trading-bot.git
   cd Discord-Telegram-notification-trading-bot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Create a configuration file** in the `config/` directory with your credentials:
   ```python
   # config/settings.py
   DISCORD_TOKEN = "your-discord-bot-token"
   DISCORD_CHANNEL_ID = "your-channel-id"
   
   TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
   TELEGRAM_CHAT_ID = "your-chat-id"
   
   TRADINGVIEW_API_KEY = "your-api-key"
   
   N8N_WEBHOOK_URL = "your-n8n-webhook-url"
   ```

2. **Update strategy parameters** in `src/strategy.py`:
   - Adjust indicator thresholds
   - Set risk management parameters
   - Configure alert sensitivity

## 🎯 Usage

### Run the Bot

```bash
python src/Trading\ Bot\ Brain.\ regular.py
```

### Run Tests

```bash
python test_tradingview.py
python src/test_multiple.py
```

### Command Line Options

```bash
# Run with specific strategy
python src/strategy.py --strategy aggressive

# Backtest on historical data
python src/data_fetcher.py --backtest --symbol BTCUSD --period 1m

# Analyze single symbol
python src/indicators.py --symbol ETHUSDT
```

## 📊 API Integrations

### TradingView API
- Fetches real-time market data
- Supports multiple trading pairs (forex, crypto, stocks)
- Historical data for backtesting

### Discord Integration
- Real-time trade alerts
- Charts and technical analysis snapshots
- Performance summaries

### Telegram Integration
- Mobile-friendly notifications
- Quick signal alerts
- Trade confirmation updates

### N8N Automation
- Automated workflow triggers
- Integration with external services
- Advanced notification routing

## 📈 Technical Indicators

The bot analyzes multiple technical indicators including:

- **Moving Averages** (SMA, EMA)
- **Relative Strength Index (RSI)**
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **Stochastic Oscillator**
- **Heikin Ashi Candles** (Custom implementation)
- **Williams Alligator**
- **Vortex Indicator**

Each indicator contributes to an overall scoring system (points-based) to determine signal confidence.

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Disclaimer**: This bot is for educational purposes. Trading and investing involve substantial risk of loss. Always test thoroughly and never risk capital you cannot afford to lose.