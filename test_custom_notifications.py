"""
Enhanced Discord Notification Customizer
==========================================
Shows how to customize notification messages with custom fields, colors, and formatting.
"""

import asyncio
from datetime import datetime
from src.discord_notifier import DiscordNotifier, SignalType
import os
from dotenv import load_dotenv

load_dotenv()

async def demonstrate_customized_notifications():
    """Demonstrate various customization options for Discord notifications."""
    
    # Initialize notifier
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    notifier = DiscordNotifier(webhook_url=webhook_url, bot_token=bot_token)
    
    print("\n" + "="*70)
    print("DISCORD NOTIFICATION CUSTOMIZATION DEMO")
    print("="*70)
    
    try:
        # ===== EXAMPLE 1: Strong BUY Signal with Multiple Indicators =====
        print("\n[1] Sending STRONG BUY signal with full indicators...")
        await notifier.send_buy_signal(
            ticker="TSLA",
            price=245.50,
            confidence=0.92,  # 92% confidence
            indicators={
                "Alligator_Trend": "UP ⬆️",
                "Stoch_RSI": "47.5",
                "Vortex_VI": "Positive",
                "Breakout": "Validated ✓",
                "Volume": "2.5M shares",
                "RSI": "65",
                "MACD": "Bullish Cross"
            }
        )
        print("✓ BUY signal sent with comprehensive indicators!")
        
        # ===== EXAMPLE 2: SELL Signal with Risk Assessment =====
        print("\n[2] Sending SELL signal with risk indicators...")
        await notifier.send_sell_signal(
            ticker="NVDA",
            price=135.75,
            confidence=0.78,  # 78% confidence
            indicators={
                "Alligator_Trend": "DOWN ⬇️",
                "Stoch_RSI": "78.2",
                "Vortex_VI": "Negative",
                "Support_Level": "$130.00",
                "Resistance": "$140.00",
                "Volume_Change": "+35%",
                "Risk_Reward": "1:2.5"
            }
        )
        print("✓ SELL signal sent with risk analysis!")
        
        # ===== EXAMPLE 3: Market Alert =====
        print("\n[3] Sending market alert notification...")
        await notifier.send_alert(
            "🚨 MARKET ALERT: Federal Reserve decision announced. Increased volatility expected. Position reviews recommended.",
            ticker="MARKET"
        )
        print("✓ Market alert sent!")
        
        # ===== EXAMPLE 4: Multi-Signal Summary =====
        print("\n[4] Sending daily trading summary...")
        summary_message = """
📊 **DAILY TRADING SUMMARY** - February 6, 2026

📈 **Bullish Signals (3)**
├─ AAPL: Reversal pattern confirmed
├─ AMD: Breakout above resistance
└─ TSM: Volume surge detected

📉 **Bearish Signals (2)**
├─ META: Breakdown below support
└─ INTC: Declining momentum

⊙ **Hold/Monitor (5)**
├─ MSFT: Consolidation phase
├─ GOOGL: Neutral zone
├─ AMZN: Waiting for breakout
├─ NVDA: Watching resistance
└─ CRM: Technical indecision

**Market Sentiment:** Mixed (40% Bullish, 30% Bearish, 30% Neutral)
**Next Event:** FOMC Meeting - Friday 2 PM ET
        """
        await notifier.send_alert(summary_message)
        print("✓ Daily summary sent!")
        
        # ===== EXAMPLE 5: Technical Analysis with Custom Indicators =====
        print("\n[5] Sending detailed technical analysis...")
        await notifier.send_signal(
            signal_type=SignalType.ALERT,
            ticker="SPY",
            price=589.25,
            confidence=0.85,
            indicators={
                "🔴 Resistance_1": "$595.00 (Key Level)",
                "🔴 Resistance_2": "$605.00 (Psychological)",
                "🟢 Support_1": "$580.00 (Strong)",
                "🟢 Support_2": "$570.00 (Major)",
                "📊 Moving_Average_50": "$575.50",
                "📊 Moving_Average_200": "$560.25",
                "📈 Trend_Strength": "Moderate (Score: 7/10)",
                "⚡ Next_Catalyst": "CPI Report (Tue 8:30 AM)"
            },
            description="📈 SPY Daily Technical Setup - Ready for breakout?"
        )
        print("✓ Technical analysis sent!")
        
        # ===== EXAMPLE 6: Error/Risk Alert =====
        print("\n[6] Sending error notification...")
        await notifier.send_error("⚠️ Data sync failed with broker API. Reconnecting in 30 seconds...", ticker="SYS")
        print("✓ Error alert sent!")
        
        print("\n" + "="*70)
        print("✓ ALL CUSTOMIZATION EXAMPLES SENT TO DISCORD")
        print("="*70)
        print("\n💡 KEY FEATURES DEMONSTRATED:")
        print("   • Custom confidence levels (0.0 - 1.0)")
        print("   • Multiple indicator fields with custom formatting")
        print("   • Color-coded signals (🟢 Green=BUY, 🔴 Red=SELL, 🟡 Yellow=ALERT)")
        print("   • Detailed descriptions and risk assessment")
        print("   • Market summaries and batch updates")
        print("   • Error notifications with severity levels")
        print("\n🎯 USE CASES:")
        print("   1. Real-time trading alerts - Send on signal detection")
        print("   2. Daily reports - Send market summaries at EOD")
        print("   3. Risk management - Alert on unusual volatility")
        print("   4. Portfolio monitoring - Track watchlist changes")
        print("   5. System monitoring - Notify on connectivity issues")
        
        await notifier.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demonstrate_customized_notifications())
