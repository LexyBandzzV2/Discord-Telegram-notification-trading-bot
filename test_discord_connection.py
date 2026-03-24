#!/usr/bin/env python3
"""
Diagnostic test to check Discord bot connectivity and signal sending.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.discord_notifier import DiscordNotifier, SignalType
from datetime import datetime

async def test_discord_connection():
    """Test Discord bot connection and message sending."""
    
    print("="*80)
    print("🔍 DISCORD BOT DIAGNOSTIC TEST")
    print("="*80)
    print()
    
    # Load config
    config = Config()
    
    print("✓ Step 1: Checking Configuration")
    print(f"  Bot Token: {'✅ SET' if config.DISCORD_BOT_TOKEN else '❌ NOT SET'}")
    print(f"  Bot Token Length: {len(config.DISCORD_BOT_TOKEN)} chars")
    print(f"  Commands Channel: {config.DISCORD_COMMANDS_CHANNEL}")
    print()
    
    print("✓ Step 2: Checking Discord Channels")
    for timeframe, channel_id in config.DISCORD_CHANNELS.items():
        print(f"  {timeframe}: {channel_id}")
    print()
    
    print("✓ Step 3: Initializing Discord Notifier")
    try:
        notifier = DiscordNotifier(
            bot_token=config.DISCORD_BOT_TOKEN,
            channels=config.DISCORD_CHANNELS
        )
        print("  ✅ Notifier initialized successfully")
    except Exception as e:
        print(f"  ❌ Failed to initialize notifier: {e}")
        return
    print()
    
    print("✓ Step 4: Testing Discord API Connection")
    print("  Sending test BUY signal to 1H channel...")
    
    try:
        # Try to send a test signal
        success = await notifier.send_buy_signal(
            ticker='TSLA',
            ticker_display='🚗 Tesla',
            price=397.10,
            timeframe='1h',
            confidence=0.85,
            indicators={
                'price': 397.10,
                'stoch_k': 75.5,
                'stoch_d': 72.3,
                'stoch_status': 'Overbought (touching 80+ line)',
                'alligator_status': 'Green line crossing upward over red line and blue line',
                'vortex_status': 'Green cross - VI+ crossing above VI- (uptrend)'
            }
        )
        
        if success:
            print("  ✅ Test message sent successfully!")
        else:
            print("  ❌ Send returned False - check Discord API permissions")
    except Exception as e:
        print(f"  ❌ Error sending test message: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("✓ Step 5: Testing SELL Signal")
    print("  Sending test SELL signal to 15m channel...")
    
    try:
        success = await notifier.send_sell_signal(
            ticker='BTC-USD',
            ticker_display='₿ Bitcoin',
            price=62978.68,
            timeframe='15m',
            confidence=0.87,
            indicators={
                'price': 62978.68,
                'stoch_k': 18.5,
                'stoch_d': 22.1,
                'stoch_status': 'Oversold (touching 20- line)',
                'alligator_status': 'Green line crossing downward below red line',
                'vortex_status': 'Red cross - VI- crossing above VI+ (downtrend)'
            }
        )
        
        if success:
            print("  ✅ Test SELL signal sent successfully!")
        else:
            print("  ❌ Send returned False")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    await notifier.close()
    
    print()
    print("="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    print()
    print("If you saw ✅ on both signals above, your bot is working!")
    print("If you saw ❌, check:")
    print("  1. Bot token is correct in .env")
    print("  2. Bot has 'Send Messages' permission in those channels")
    print("  3. Channel IDs are correct")
    print()

if __name__ == "__main__":
    asyncio.run(test_discord_connection())
