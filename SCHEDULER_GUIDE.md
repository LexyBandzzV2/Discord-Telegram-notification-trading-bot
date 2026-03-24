# Scheduled Trading Bot - Complete Setup Guide

## 🚀 Overview

Your trading bot now runs **automatically every weekday at 9:00 AM EST** (market open) to analyze all tickers and send Discord notifications.

---

## 📅 Schedule Details

| Setting | Value |
|---------|-------|
| **Time** | 9:00 AM EST |
| **Days** | Monday - Friday |
| **Timezone** | US/Eastern |
| **Frequency** | Daily (on weekdays only) |
| **Action** | Multi-timeframe analysis + Discord notifications |

---

## 🎯 What Happens at 9 AM

Every weekday at 9:00 AM EST:

1. ✅ **Fetches Market Data**
   - Downloads latest prices for all 7 tickers
   - TSLA, BTC-USD, AAPL, ETH-USD, ^GSPC, XRP-USD, NVDA

2. ✅ **Analyzes 5 Timeframes**
   - 1-minute (⚡)
   - 3-minute (🔥)
   - 5-minute (📊)
   - 15-minute (📈)
   - 1-hour (🕐)

3. ✅ **Generates Trading Signals**
   - BUY signals (🟢)
   - SELL signals (🔴)
   - Confidence scores (0-100%)

4. ✅ **Sends Discord Notifications**
   - Routes to correct timeframe channel
   - Includes price, confidence, indicators
   - All in formatted embeds

---

## 📖 How to Run the Scheduler

### **Method 1: Python Command (Recommended)**

```bash
# Start the scheduler (will run indefinitely)
python scheduler.py

# Test analysis immediately
python scheduler.py --test

# Show schedule information
python scheduler.py --show-schedule
```

### **Method 2: Batch File (Windows)**

```bash
# Double-click: run_scheduler.bat
# or from command line:
run_scheduler.bat
```

### **Method 3: Task Scheduler (Windows - Auto-Start)**

For the bot to run automatically when Windows boots:

1. **Create Batch File**
   - Create `start_bot.bat` in project folder:
   ```batch
   @echo off
   cd /d "%~dp0"
   .venv\Scripts\python.exe scheduler.py
   ```

2. **Add to Windows Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`
   - Click "Create Basic Task"
   - **Name:** Trading Bot Scheduler
   - **Trigger:** At startup (or specific time)
   - **Action:** Start program → Browse to `start_bot.bat`
   - **Settings:** Check "Run whether user is logged in"

3. **Or use PowerShell:**
   ```powershell
   # Run as Administrator
   $action = New-ScheduledTaskAction -Execute "C:\...\start_bot.bat"
   $trigger = New-ScheduledTaskTrigger -AtStartup
   Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "TradingBotScheduler" -RunLevel Highest
   ```

---

## 🧪 Testing the Scheduler

### **Run Analysis Now (Test)**
```bash
python scheduler.py --test
```
This runs the full analysis immediately without waiting for 9 AM.

### **View Schedule**
```bash
python scheduler.py --show-schedule
```
Shows when the next run will occur.

### **Monitor Live**
```bash
python scheduler.py
```
Starts the scheduler and waits for the next 9 AM run. Console shows:
- Current time
- Next scheduled run time
- Live updates when analysis runs

---

## 📊 Output & Notifications

### **Console Output**
When the scheduler runs, you'll see:
```
================================================================================
⏰ SCHEDULED ANALYSIS - 2026-02-07 09:00:00
================================================================================

📊 Analyzing TSLA on 1m... ⊙ Hold
📊 Analyzing TSLA on 5m... ✓ SELL
📊 Analyzing AAPL on 1h... ✓ BUY
...

✅ Scheduled analysis complete
```

### **Discord Notifications**
Each signal generates a formatted embed sent to the correct channel:
- **#trading-1min:** 1-minute signals
- **#trading-3min:** 3-minute signals
- **#trading-5min:** 5-minute signals
- **#trading-15min:** 15-minute signals
- **#trading-1hour:** 1-hour signals

---

## 🔧 Configuration

### **Change Schedule Time**

Edit `scheduler.py` line ~94:
```python
trigger = CronTrigger(
    hour=9,           # ← Change hour (0-23)
    minute=0,         # ← Change minute (0-59)
    day_of_week='mon-fri',
    timezone=tz
)
```

**Examples:**
- 8:30 AM: `hour=8, minute=30`
- 10:00 AM: `hour=10, minute=0`
- 4:00 PM (market close): `hour=16, minute=0`

### **Change Timezone**

Line ~87:
```python
tz = pytz.timezone('US/Eastern')  # ← Change timezone
```

**Common timezones:**
- `US/Eastern` - New York
- `US/Central` - Chicago
- `US/Mountain` - Denver
- `US/Pacific` - Los Angeles
- `Europe/London` - London
- `Europe/Paris` - Paris
- `Asia/Tokyo` - Tokyo

### **Add More Days**

Line ~96:
```python
day_of_week='mon-fri',  # ← Change days
```

**Options:**
- `'mon-fri'` - Weekdays only
- `'0-6'` - Every day (0=Monday, 6=Sunday)
- `'0,2,4'` - Specific days (Mon, Wed, Fri)

---

## 📝 Logs & Monitoring

### **View Recent Runs**
The scheduler logs all runs. Check console output for:
- Time of execution
- Number of signals generated
- Discord send status

### **Keep Logs**
To save logs to file, modify `scheduler.py`:
```python
import logging

logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
```

---

## 🛠️ Troubleshooting

### **"Scheduler not running"**
- Check timezone is correct (US/Eastern for EST)
- Verify 9 AM hasn't already passed today
- Scheduler skips past runs automatically

### **"Discord notifications not sending"**
- Run: `python test_discord_setup.py` to test
- Check `.env` has correct bot token and channel IDs
- Verify bot has message permissions in Discord

### **"No market data available"**
- Yahoo Finance may be down
- Try different data provider: `DATA_PROVIDER=alpaca`
- Check internet connection

### **"Port already in use"**
- Only one scheduler instance should run
- Check Task Manager for duplicate processes

---

## 💡 Advanced Usage

### **Run Multiple Analyses**

Add additional time slots (e.g., 9 AM and 3 PM):

```python
# In scheduler.py, after scheduling first job:

# Add second job for market close
trigger2 = CronTrigger(
    hour=15,  # 3 PM
    minute=0,
    day_of_week='mon-fri',
    timezone=tz
)

self.scheduler.add_job(
    self._async_wrapper,
    trigger=trigger2,
    id='market_close_analysis',
    name='Market Close Analysis (3 PM EST)',
)
```

### **Add Email Alerts**

Modify `src/multi_timeframe_analyzer.py` to send emails:
```python
import smtplib

async def send_email_alert(signal):
    # Email code here
    pass
```

### **Integrate with Trading Platform**

Add auto-execution to Alpaca/IBKR:
```python
from alpaca.trading.client import TradingClient

api = TradingClient(API_KEY, SECRET_KEY)

if signal == 'BUY':
    api.submit_order(symbol='AAPL', qty=10, side='buy')
```

---

## 📋 Checklist

- [x] Scheduler installed (`apscheduler` + `pytz`)
- [x] `scheduler.py` created and tested
- [x] 9 AM EST schedule configured
- [x] Weekdays (Mon-Fri) selected
- [x] All 7 tickers configured
- [x] 5 timeframes active
- [x] Discord channels linked
- [x] Test run successful
- [ ] Running 24/7 (use Task Scheduler)
- [ ] Monitor first live run at 9 AM

---

## 🚀 Next Steps

1. **Run the scheduler:**
   ```bash
   python scheduler.py
   ```

2. **Wait for 9 AM tomorrow** (or run `--test` now)

3. **Check Discord** for trading signals in your timeframe channels

4. **Set up Windows Task Scheduler** to run automatically on system startup

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| **Start scheduler** | `python scheduler.py` |
| **Test now** | `python scheduler.py --test` |
| **Show schedule** | `python scheduler.py --show-schedule` |
| **Test Discord** | `python test_discord_setup.py` |
| **Full analysis test** | `python test_multi_timeframe.py` |

---

**Your trading bot will now run automatically at 9 AM EST every weekday!** 🤖📈

Generated: February 6, 2026
Version: 1.0
Status: ✅ OPERATIONAL
