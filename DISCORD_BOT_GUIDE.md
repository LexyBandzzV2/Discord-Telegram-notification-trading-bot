# Discord Bot Commands - Complete Guide

## 🤖 Overview

Your trading bot now has **Discord commands** to run analysis on-demand directly from Discord. Commands are entered in any channel and signals are automatically posted to the appropriate timeframe channels.

---

## 🚀 Getting Started

### **Start the Bot**

```bash
python discord_bot.py
```

You should see:
```
✅ Bot connected as Trading Bot
   Prefix: !
   Watching for commands...
```

### **Create a Bot Commands Channel** (Optional)

Create a channel like `#bot-commands` or `#trading-commands` where users can run commands. While not required, it helps organize your server.

---

## 📝 Available Commands

### **1. Analyze Single Ticker**

Analyze any of your monitored assets:

```
!analyze TSLA
!analyze AAPL
!analyze BTC
!analyze ETH
!analyze XRP
!analyze NVDA
!analyze SP500
```

**Also supports aliases:**
```
!analyze TESLA      # → TSLA
!analyze BITCOIN    # → BTC-USD
!analyze APPLE      # → AAPL
!analyze ETHEREUM   # → ETH-USD
!analyze RIPPLE     # → XRP-USD
!analyze NVIDIA     # → NVDA
!analyze SP500      # → ^GSPC
```

**Response:**
- Shows analysis progress in Discord
- Runs analysis on all 5 timeframes (1m, 3m, 5m, 15m, 1h)
- Posts signals to correct channels automatically
- Shows summary with signal counts per timeframe

**Example:**
```
User: !analyze TSLA

Bot: 🔄 Running Analysis
     Analyzing 🚗 Tesla...
     Tickers: TSLA
     Timeframes: 1m, 3m, 5m, 15m, 1h
     
     [analysis runs...]
     
     ✅ Analysis Complete
     📈 Total Signals: 1 signals generated
     
     By Timeframe:
     ⚡ 1M: 0 signals
     🔥 3M: 0 signals
     📊 5M: 0 signals
     📈 15M: 0 signals
     🕐 1H: 1 signals
```

---

### **2. Full Market Analysis**

Analyze all 7 assets at once:

```
!analyze all
```

**What it does:**
- Analyzes: TSLA, BTC, AAPL, ETH, ^GSPC, XRP, NVDA
- Runs on all 5 timeframes
- Generates all available signals
- Posts everything to Discord
- Shows comprehensive summary

**Example:**
```
User: !analyze all

Bot: 🔄 Running Analysis
     Analyzing all 7 assets...
     
     [analyzes each ticker and timeframe...]
     
     ✅ Analysis Complete
     📈 Total Signals: 11 signals generated
     
     By Timeframe:
     ⚡ 1M: 1 signals
     🔥 3M: 0 signals
     📊 5M: 1 signals
     📈 15M: 3 signals
     🕐 1H: 6 signals
```

---

### **3. Bot Status**

Show bot status and configuration:

```
!status
```

**Shows:**
- ✅ Bot connection status
- 📊 Assets being monitored
- ⏱️ Timeframes analyzed
- 📅 Scheduled run times
- 🕐 Current time
- 💻 System info (data provider, debug mode)

---

### **4. List Tickers**

Show all monitored assets:

```
!tickers
```

**Shows:**
- All 7 monitored assets with their ticker symbols
- Quick command examples

---

### **5. View Schedule**

Show when the bot runs automatically:

```
!schedule
```

**Shows:**
- Run time: 9:00 AM EST
- Days: Monday - Friday
- What happens (full market analysis)
- How to run manually

---

### **6. Help**

Display all available commands:

```
!help
```

---

## 📊 Command Workflow

### **When You Run `!analyze TSLA`:**

1. **Input:** You type `!analyze TSLA` in Discord
2. **Validation:** Bot checks ticker is valid
3. **Status:** Bot shows "🔄 Running Analysis..."
4. **Analysis:** Bot analyzes TSLA on all 5 timeframes
5. **Signals:** Any signals detected are sent to their channels:
   - 1M signals → #trading-1min
   - 3M signals → #trading-3min
   - 5M signals → #trading-5min
   - 15M signals → #trading-15min
   - 1H signals → #trading-1hour
6. **Summary:** Bot shows final summary in your command channel
   - Total signals found
   - Breakdown by timeframe

---

## 💡 Tips & Best Practices

### **Quick Analysis**

For fastest results, analyze a single ticker:
```
!analyze TSLA    # ~30 seconds
```

Instead of all assets:
```
!analyze all     # ~2-3 minutes
```

### **During Market Hours**

Run commands during market hours (9:30 AM - 4:00 PM EST) for most accurate data.

### **Check Status Before Trading**

Before making a trade decision, run:
```
!analyze TSLA    # Get latest signals
!status          # Verify bot is running
```

### **Track Results**

Keep `#trading-signals` or similar channel to review all alerts in one place (Discord's pinning feature helps).

---

## 🔧 Configuration

### **Command Prefix**

Default prefix is `!`. To change it, edit `discord_bot.py` line 38:
```python
bot = commands.Bot(command_prefix='!', intents=intents)
                                      ↑
                              Change to: '/', '>', '~', etc.
```

### **Add More Tickers**

Edit `config/config.py`:
```python
PRIMARY_TICKERS = ['TSLA', 'BTC-USD', 'AAPL', 'ETH-USD', '^GSPC', 'XRP-USD', 'NVDA', 'YOUR_TICKER']
```

And add display name:
```python
TICKER_NAMES = {
    ...
    'YOUR_TICKER': '🆕 Your Asset Name',
}
```

### **Add Ticker Aliases**

Edit `discord_bot.py` TICKER_MAP (line ~45):
```python
TICKER_MAP = {
    ...
    'youralias': 'YOUR_TICKER',
    'shortname': 'YOUR_TICKER',
}
```

---

## ❌ Error Handling

### **Invalid Ticker**
```
!analyze XYZ

Bot: ❌ Invalid Ticker
     `XYZ` is not in the watchlist
     Available Tickers: TSLA, BTC-USD, AAPL, ...
```

### **Wrong Channel** (Optional Warning)
```
Bot: ❌ Please use this command in a bot-commands or commands channel.
```

### **Analysis Error**
```
Bot: ❌ Analysis Failed
     Error: [error details]
```

---

## 📈 Example Session

```
User: !status
Bot: [Shows bot status - all green ✅]

User: !analyze all
Bot: 🔄 Running Analysis...
     [50 seconds pass]
Bot: ✅ Analysis Complete
     📈 Total Signals: 11
     ⚡ 1M: 1 | 🔥 3M: 0 | 📊 5M: 1 | 📈 15M: 3 | 🕐 1H: 6

[In #trading-1hour channel]
Bot: 🔴 SELL SIGNAL: 🚗 Tesla
     💰 Price: $397.10
     ⏱️ Timeframe: 1H
     📊 Confidence: 88%

[In #trading-15min channel]
Bot: 🔴 SELL SIGNAL: ₿ Bitcoin
     💰 Price: $62,978.68
     ⏱️ Timeframe: 15M
     📊 Confidence: 87%
```

---

## 🚀 Integration with Scheduler

The Discord bot **complements** your scheduled runs:

| Scenario | Use |
|----------|-----|
| **Scheduled (9 AM)** | `scheduler.py` - Automatic analysis |
| **During Day** | `!analyze TSLA` - Quick check |
| **Before Trade** | `!analyze all` - Full market check |
| **Monitoring** | `!status` - Check bot is running |

---

## 📋 Checklist

- [x] Bot created with commands
- [x] Single ticker analysis (`!analyze TSLA`)
- [x] Full market analysis (`!analyze all`)
- [x] Status command (`!status`)
- [x] Schedule info (`!schedule`)
- [x] Help command (`!help`)
- [x] Error handling
- [x] Tests passed
- [ ] Bot running continuously
- [ ] Discord server configured
- [ ] Commands tested in Discord

---

## 🔗 Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `!analyze <ticker>` | Analyze one asset | `!analyze TSLA` |
| `!analyze all` | Analyze all 7 assets | `!analyze all` |
| `!status` | Show bot status | `!status` |
| `!tickers` | List monitored assets | `!tickers` |
| `!schedule` | Show run schedule | `!schedule` |
| `!help` | Show all commands | `!help` |

---

**Your bot is ready for on-demand Discord commands!** 🤖

To start: `python discord_bot.py`

Generated: February 6, 2026
Version: 1.0
Status: ✅ READY
