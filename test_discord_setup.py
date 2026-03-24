"""
Quick Test Script for Discord Notifications
============================================
Tests the Discord bot and webhook functionality.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.discord_notifier import DiscordNotifier

async def test_discord_notifications():
    """Test Discord notifications with sample data"""
    
    # Get credentials from environment
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not webhook_url and not bot_token:
        print("❌ Error: No Discord credentials found in .env file")
        print("Please ensure .env file has DISCORD_WEBHOOK_URL or DISCORD_BOT_TOKEN")
        return
    
    # Initialize Discord notifier
    notifier = DiscordNotifier(webhook_url=webhook_url, bot_token=bot_token)
    
    print("🤖 Testing Discord Notifications...")
    print("=" * 50)
    
    try:
        # Test 1: Send a BUY signal
        print("\n📈 Test 1: Sending BUY signal...")
        await notifier.send_buy_signal(
            ticker="AAPL",
            price=150.25,
            confidence=0.85,
            indicators={"RSI": "65", "MACD": "Positive"}
        )
        print("✅ BUY signal sent!")
        
        # Test 2: Send a SELL signal
        print("\n📉 Test 2: Sending SELL signal...")
        await notifier.send_sell_signal(
            ticker="MSFT",
            price=320.50,
            confidence=0.75,
            indicators={"RSI": "75", "Stoch": "Overbought"}
        )
        print("✅ SELL signal sent!")
        
        # Test 3: Send a general alert
        print("\n⚠️ Test 3: Sending general alert...")
        await notifier.send_alert("📡 Trading bot initialized and ready to go!")
        print("✅ Alert message sent!")
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("=" * 50)
        
        # Close the session
        await notifier.close()
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run async tests
    asyncio.run(test_discord_notifications())
