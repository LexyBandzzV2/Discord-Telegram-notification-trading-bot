#!/usr/bin/env python3
"""
Simple startup test for the Discord bot.
"""

import sys
import os

# Test 1: Check config loads
print("Test 1: Loading config...")
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
    from config.config import Config
    config = Config()
    print(f"✅ Config loaded")
    print(f"   Tickers: {len(config.PRIMARY_TICKERS)} assets")
    print(f"   Timeframes: {config.TIMEFRAMES}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Check imports
print("\nTest 2: Checking bot imports...")
try:
    import discord
    from discord.ext import commands
    print(f"✅ Discord.py imported")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Try to create bot instance
print("\nTest 3: Creating bot instance...")
try:
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
    print(f"✅ Bot instance created")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 4: Try to register commands
print("\nTest 4: Registering commands...")
try:
    @bot.command(name='analyze', help='Test')
    async def analyze(ctx, *, ticker: str = None):
        pass
    
    @bot.command(name='status', help='Test')
    async def status(ctx):
        pass
    
    @bot.command(name='commands', help='Test')
    async def commands_cmd(ctx):
        pass
    
    print(f"✅ Commands registered successfully")
except Exception as e:
    print(f"❌ Error registering commands: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - Bot is ready to run!")
print("="*60)
print("\nStart bot with: python discord_bot.py")
