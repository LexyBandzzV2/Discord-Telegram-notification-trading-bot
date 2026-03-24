"""
Discord Notification Test Script
==================================
Tests Discord integration without running the full trading bot.

Usage:
    python test_discord.py
"""

import sys
import os
import asyncio

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.discord_notifier import DiscordNotifier, SignalType


async def test_discord():
    """Test Discord notifications."""
    config = Config()
    
    print("\n" + "="*70)
    print("DISCORD NOTIFICATION TEST")
    print("="*70)
    
    # Check configuration
    is_valid, message = config.validate()
    print(f"\nConfiguration Status: {message}")
    
    if not config.DISCORD_ENABLED:
        print("\n❌ Discord is not enabled.")
        print("   Please set DISCORD_WEBHOOK_URL or (DISCORD_BOT_TOKEN + DISCORD_CHANNEL_ID)")
        return False
    
    print("\n✓ Discord is enabled. Testing notifications...\n")
    
    try:
        # Initialize notifier
        notifier = DiscordNotifier(
            webhook_url=config.DISCORD_WEBHOOK_URL,
            bot_token=config.DISCORD_BOT_TOKEN,
            channel_id=config.DISCORD_CHANNEL_ID
        )
        
        # Test 1: Buy Signal
        print("[TEST 1] Sending test BUY signal...")
        buy_result = await notifier.send_buy_signal(
            ticker='AAPL',
            price=150.25,
            confidence=0.85,
            indicators={
                'RSI': '65.5',
                'MACD': 'Positive',
                'Trend': 'Bullish'
            }
        )
        if buy_result:
            print("✓ BUY signal sent successfully\n")
        else:
            print("❌ Failed to send BUY signal\n")
            return False
        
        # Test 2: Sell Signal
        print("[TEST 2] Sending test SELL signal...")
        sell_result = await notifier.send_sell_signal(
            ticker='TSLA',
            price=245.75,
            confidence=0.72,
            indicators={
                'RSI': '72.3',
                'MACD': 'Negative',
                'Trend': 'Bearish'
            }
        )
        if sell_result:
            print("✓ SELL signal sent successfully\n")
        else:
            print("❌ Failed to send SELL signal\n")
            return False
        
        # Test 3: Alert
        print("[TEST 3] Sending test ALERT...")
        alert_result = await notifier.send_alert(
            message="🔔 This is a test alert from the trading bot notification system.",
            ticker='TEST'
        )
        if alert_result:
            print("✓ ALERT sent successfully\n")
        else:
            print("❌ Failed to send ALERT\n")
            return False
        
        # Test 4: Error
        print("[TEST 4] Sending test ERROR notification...")
        error_result = await notifier.send_error(
            error_message="This is a test error message from the trading bot.",
            ticker='TEST'
        )
        if error_result:
            print("✓ ERROR notification sent successfully\n")
        else:
            print("❌ Failed to send ERROR notification\n")
            return False
        
        await notifier.close()
        
        print("="*70)
        print("✓ ALL TESTS PASSED!")
        print("="*70)
        print("\nYour Discord notifications are working correctly.")
        print("You can now run the trading bot with: python main.py --ticker AAPL --start 2024-01-01")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test entry point."""
    try:
        result = asyncio.run(test_discord())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1


if __name__ == '__main__':
    exit(main())
