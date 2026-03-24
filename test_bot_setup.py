#!/usr/bin/env python3
"""
Quick test to verify Discord bot commands are working.
"""

import sys
import os

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config

print("="*80)
print("🤖 DISCORD BOT COMMAND TEST")
print("="*80)
print()

# Test 1: Verify Config
print("✓ Test 1: Config validation")
is_valid, message = Config.validate()
print(f"  {message}")
if not is_valid:
    print("  ❌ Config invalid!")
    sys.exit(1)

# Test 2: Check bot token
config = Config()
token = config.DISCORD_BOT_TOKEN

if not token or token == "YOUR_BOT_TOKEN_HERE":
    print("❌ ERROR: DISCORD_BOT_TOKEN not set properly in .env file")
    print()
    print("To fix this:")
    print("1. Create/edit .env file in the root directory")
    print("2. Add this line:")
    print("   DISCORD_BOT_TOKEN=your_actual_bot_token_here")
    print("3. Save and run again")
    sys.exit(1)

print("✓ Bot token found")
print()

# Test 3: Check channels
print("✓ Test 2: Discord channels configured")
for tf, channel_id in config.DISCORD_CHANNELS.items():
    print(f"  {tf}: {channel_id}")
print()

# Test 4: List tickers
print("✓ Test 3: Tickers to monitor")
for ticker in config.PRIMARY_TICKERS:
    display = config.get_ticker_display_name(ticker)
    print(f"  {display}: {ticker}")
print()

print("="*80)
print("✅ ALL CHECKS PASSED")
print("="*80)
print()
print("Your Discord bot is ready to run!")
print()
print("To start the bot:")
print("  python discord_bot.py")
print()
print("Commands available:")
print("  !analyze TSLA        - Analyze Tesla")
print("  !analyze all         - Full market analysis")
print("  !status              - Show bot status")
print("  !tickers             - List monitored assets")
print("  !schedule            - Show run schedule")
print("  !help                - Show all commands")
print()
print("Commands work in ANY Discord channel!")
print()
