# Discord Trading Bot Setup Guide

## 🎯 Quick Start

This guide walks you through setting up and running the trading bot with Discord notifications.

---

## 📋 Prerequisites

- **Python 3.8+** installed
- **Discord Server** (where you want to receive notifications)
- **Discord Bot or Webhook** (created in your Discord Server)

---

## 🔧 Step 1: Set Up Discord Notifications

You have two options for Discord integration:

### **Option A: Discord Webhook (Simpler)**

1. **Create a Webhook in your Discord Server:**
   - Open your Discord server
   - Go to **Server Settings** → **Integrations** → **Webhooks**
   - Click **Create Webhook**
   - Name it "Trading Bot"
   - Select the channel where you want notifications
   - Copy the **Webhook URL**

2. **Add to .env file:**
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
   ```

### **Option B: Discord Bot (More Control)**

1. **Create a Discord Bot:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click **New Application**
   - Go to **Bot** → **Add Bot**
   - Under **TOKEN**, click **Copy** to copy your bot token

2. **Configure Bot Permissions:**
   - Go to **OAuth2** → **URL Generator**
   - Select scopes: `bot`
   - Select permissions: `Send Messages`, `Embed Links`, `Read Message History`
   - Copy the generated URL and open it to add the bot to your server

3. **Get Your Channel ID:**
   - Enable **Developer Mode** in Discord (User Settings → Advanced → Developer Mode)
   - Right-click any channel and select **Copy Channel ID**

4. **Add to .env file:**
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_CHANNEL_ID=your_channel_id_here
   ```

---

## 📦 Step 2: Install Dependencies

1. **Clone or download the project** (already done)

2. **Create virtual environment (optional but recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Step 3: Configure Environment Variables

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file** with your settings:
   ```
   # Choose ONE Discord option:
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   # OR
   DISCORD_BOT_TOKEN=your_bot_token
   DISCORD_CHANNEL_ID=your_channel_id
   
   # Data provider (yahoo is default and free)
   DATA_PROVIDER=yahoo
   
   # Optional: Add API keys for other providers
   # IBKR_HOST=127.0.0.1
   # IBKR_PORT=7497
   # ALPACA_API_KEY=...
   ```

---

## ✅ Step 4: Test Discord Integration

Before running the full bot, test your Discord setup:

```bash
python test_discord.py
```

**Expected Output:**
```
[TEST 1] Sending test BUY signal...
✓ BUY signal sent successfully

[TEST 2] Sending test SELL signal...
✓ SELL signal sent successfully

[TEST 3] Sending test ALERT...
✓ ALERT sent successfully

[TEST 4] Sending test ERROR notification...
✓ ERROR notification sent successfully

✓ ALL TESTS PASSED!
```

Check your Discord channel - you should see 4 colored embeds with trading signals!

---

## 🚀 Step 5: Run the Trading Bot

### **Basic Usage:**
```bash
# Analyze a single ticker
python main.py --ticker AAPL --start 2024-01-01

# With custom end date
python main.py --ticker TSLA --start 2024-01-01 --end 2024-12-31

# With different data provider
python main.py --ticker SPY --start 2024-01-01 --provider yahoo
```

### **Command Options:**
```
--ticker SYMBOL      Stock ticker symbol (required)
--start DATE        Start date YYYY-MM-DD (required)
--end DATE          End date YYYY-MM-DD (optional, defaults to today)
--provider SOURCE   Data provider: yahoo, ibkr, or alpaca (default: yahoo)
--config FILE.json  Load config from JSON file
--no-breakout-filter  Disable breakout candle filter
--check-config      Validate configuration and exit
```

### **Example Workflow:**
```bash
# 1. Check configuration
python main.py --check-config

# 2. Test Discord
python test_discord.py

# 3. Run analysis for AAPL
python main.py --ticker AAPL --start 2024-01-01

# 4. Run analysis for multiple stocks (run separately)
python main.py --ticker TSLA --start 2024-01-01
python main.py --ticker MSFT --start 2024-01-01
python main.py --ticker GOOGL --start 2024-01-01
```

---

## 📊 What Happens When You Run the Bot

1. **Fetches Historical Data** - Gets OHLCV candles from your data provider
2. **Converts to Heikin-Ashi** - Smooths price action using advanced candlestick format
3. **Calculates Indicators** - Analyzes Alligator, Stochastic RSI, Vortex, and more
4. **Generates Signals** - Finds buy/sell opportunities
5. **Sends Discord Notification** - Posts results to your Discord channel

### **Discord Notification Examples:**

**BUY Signal:**
```
🟢 BUY SIGNAL: AAPL
A buy opportunity has been detected for AAPL

💰 Price: $150.25
📊 Confidence: 85.0%
⏰ Time: 2024-01-15 14:30:45

📈 Indicators:
RSI: 65.50
MACD: Positive
Trend: Bullish
```

**SELL Signal:**
```
🔴 SELL SIGNAL: TSLA
A sell opportunity has been detected for TSLA

💰 Price: $245.75
📊 Confidence: 72.0%
⏰ Time: 2024-01-15 15:45:20

📈 Indicators:
RSI: 72.30
MACD: Negative
Trend: Bearish
```

---

## 🔍 Troubleshooting

### **"Discord is not enabled" error**
- **Solution:** Set either `DISCORD_WEBHOOK_URL` OR (`DISCORD_BOT_TOKEN` + `DISCORD_CHANNEL_ID`) in your .env file

### **"Failed to send notification" error**
- Check that your webhook URL or bot token is correct
- Verify the bot has permission to send messages in the channel
- Check your internet connection

### **No data fetched error**
- Verify the ticker symbol is correct (e.g., AAPL, not APPLE)
- Check that the date range is valid
- Ensure you have internet connection

### **Module not found error**
- Run `pip install -r requirements.txt` again
- Make sure you're in the correct directory
- If using virtual environment, ensure it's activated

---

## 🔐 Security Tips

1. **Never commit .env file** - Add it to .gitignore
2. **Use bot tokens carefully** - Rotate tokens if exposed
3. **Limit bot permissions** - Only grant necessary Discord permissions
4. **Secure API keys** - Use environment variables, never hardcode
5. **Use paper trading first** - Test with simulated trades before real money

---

## 📈 Next Steps

After setting up Discord notifications:

1. **Backtest strategies** - Analyze historical data
2. **Fine-tune indicators** - Adjust sensitivity and thresholds
3. **Monitor live trading** - Run bot on live market data
4. **Scale up** - Analyze multiple tickers simultaneously
5. **Integrate with brokers** - Connect to actual trading accounts

---

## 📚 Project Structure

```
project/
├── main.py                    # Main entry point
├── test_discord.py            # Test Discord integration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── README.md                 # Project overview
├── config/
│   └── config.py             # Configuration management
├── src/
│   ├── discord_notifier.py    # Discord integration
│   ├── data_fetcher.py        # Market data fetching
│   ├── indicators.py          # Technical indicators
│   ├── strategy.py            # Trading strategy
│   ├── Trading Bot Brain. regular.py  # Main bot logic
│   ├── Heikin Ashi.py         # Heikin-Ashi converter
│   └── n8n_api.py             # N8N integration
└── workflows/                 # N8N workflow files
```

---

## 🆘 Getting Help

- Check the **troubleshooting** section above
- Review Discord/indicator documentation
- Check logs for error messages
- Verify your configuration with `python main.py --check-config`

---

## ✨ Features

- ✓ Real-time Discord notifications
- ✓ Multiple data providers (Yahoo, IBKR, Alpaca)
- ✓ Advanced technical indicators
- ✓ Heikin-Ashi candlestick analysis
- ✓ Confidence scoring system
- ✓ Customizable signal thresholds
- ✓ Error notifications
- ✓ Easy configuration management

---

**Good luck with your trading bot! 🚀**
