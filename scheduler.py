"""
Scheduled Trading Bot
=====================
Runs scheduled tasks for LLM-enhanced trading bot:
  - 8:00am EST: Daily market news (LLM)
  - 8:30am EST: Full scan + daily summary with predictions (LLM)
  - 9:00am EST: Full chart analysis at market open

Usage:
    python scheduler.py
"""

import asyncio
import sys
import os
from datetime import datetime
import pytz
import logging

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from src.llm_wrapper import LLMWrapper
from src.strategy import get_strategy_params
from src.discord_notifier import DiscordNotifier

logger = logging.getLogger('scheduler')


class ScheduledTradingBot:
    """Manages scheduled trading bot analysis with LLM features."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.config = Config()
        self.llm = LLMWrapper(api_key=self.config.GOOGLE_API_KEY, model=self.config.LLM_MODEL)
        self.strategy_params = get_strategy_params()
        self.is_running = False
    
    async def _send_to_channel(self, channel_id: str, embed_data: dict):
        """Send an embed to a Discord channel via bot API."""
        notifier = DiscordNotifier(
            bot_token=self.config.DISCORD_BOT_TOKEN,
            channels=self.config.DISCORD_CHANNELS
        )
        await notifier.send_to_channel(channel_id, embed_data)
        await notifier.close()
    
    async def run_daily_news(self):
        """Generate and post daily market news at 8:00am EST."""
        try:
            print("\n" + "="*80)
            print(f"📰 DAILY NEWS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            
            if not self.llm.is_available:
                print("⚠️ LLM not available - skipping daily news")
                return
            
            news_text = await self.llm.generate_market_news(
                assets=self.config.PRIMARY_TICKERS,
                asset_names=self.config.TICKER_NAMES
            )
            
            embed = {
                "title": "📰 Daily Market News Briefing",
                "description": news_text[:4096],
                "color": 0x3498DB,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "footer": {"text": f"Generated {datetime.now().strftime('%B %d, %Y')} • 8:00am EST"}
            }
            
            await self._send_to_channel(self.config.DAILY_NEWS_CHANNEL, embed)
            print("✅ Daily news posted\n")
            
        except Exception as e:
            print(f"❌ Error posting daily news: {e}\n")
            import traceback
            traceback.print_exc()
    
    async def run_daily_summary(self):
        """Scan all assets and post LLM daily summary at 8:30am EST."""
        try:
            print("\n" + "="*80)
            print(f"🌅 DAILY SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            
            # Step 1: Scan all assets
            analyzer = MultiTimeframeAnalyzer(self.config)
            scan_results = await analyzer.analyze_all()
            await analyzer.close()
            
            # Step 2: Generate LLM summary
            if self.llm.is_available:
                summary_text = await self.llm.generate_daily_summary(
                    scan_results=scan_results,
                    strategy_params=self.strategy_params
                )
            else:
                total = sum(len(v) for v in scan_results.values())
                summary_text = f"Pre-market scan complete. {total} signals detected across all assets/timeframes. Set GOOGLE_API_KEY for AI predictions."
            
            # Count signals
            total = sum(len(v) for v in scan_results.values())
            buys = sum(1 for v in scan_results.values() for s in v if s.get('signal') == 'BUY')
            sells = sum(1 for v in scan_results.values() for s in v if s.get('signal') == 'SELL')
            
            embed = {
                "title": "🌅 Pre-Market Daily Summary & Predictions",
                "description": summary_text[:4096],
                "color": 0xF1C40F,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "fields": [
                    {
                        "name": "📊 Scan Results",
                        "value": f"**{total}** signals ({buys} BUY / {sells} SELL)",
                        "inline": False
                    }
                ],
                "footer": {"text": f"Market Open Summary • {datetime.now().strftime('%B %d, %Y')} • 8:30am EST"}
            }
            
            await self._send_to_channel(self.config.DAILY_SUMMARY_CHANNEL, embed)
            print("✅ Daily summary posted\n")
            
        except Exception as e:
            print(f"❌ Error posting daily summary: {e}\n")
            import traceback
            traceback.print_exc()
    
    async def run_analysis(self):
        """Run the multi-timeframe analysis at 9:00am EST."""
        try:
            print("\n" + "="*80)
            print(f"📊 MARKET OPEN ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            
            analyzer = MultiTimeframeAnalyzer(self.config)
            await analyzer.analyze_all()
            await analyzer.close()
            
            print("✅ Market open analysis complete\n")
            
        except Exception as e:
            print(f"❌ Error during market open analysis: {e}\n")
            import traceback
            traceback.print_exc()
    
    def schedule_all(self):
        """Schedule all daily tasks."""
        tz = pytz.timezone('US/Eastern')
        
        # 8:00am EST - Daily Market News
        self.scheduler.add_job(
            lambda: asyncio.run(self.run_daily_news()),
            trigger=CronTrigger(hour=8, minute=0, day_of_week='mon-fri', timezone=tz),
            id='daily_news',
            name='Daily Market News (8:00 AM EST)',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        # 8:30am EST - Daily Summary (scan + LLM predictions)
        self.scheduler.add_job(
            lambda: asyncio.run(self.run_daily_summary()),
            trigger=CronTrigger(hour=8, minute=30, day_of_week='mon-fri', timezone=tz),
            id='daily_summary',
            name='Daily Summary & Predictions (8:30 AM EST)',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        # 9:00am EST - Full Chart Analysis
        self.scheduler.add_job(
            lambda: asyncio.run(self.run_analysis()),
            trigger=CronTrigger(hour=9, minute=0, day_of_week='mon-fri', timezone=tz),
            id='market_open_analysis',
            name='Market Open Analysis (9:00 AM EST)',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        
        print("✓ Scheduled jobs created:")
        print("  📰 8:00am EST - Daily Market News → #daily-news")
        print("  🌅 8:30am EST - Daily Summary & Predictions → #daily-summary")
        print("  📊 9:00am EST - Market Open Analysis → timeframe channels")
        print()
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            print("❌ Scheduler is already running")
            return
        
        try:
            self.scheduler.start()
            self.is_running = True
            
            print("\n" + "="*80)
            print("🚀 SCHEDULED TRADING BOT STARTED")
            print("="*80)
            print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"LLM: {'✅ Enabled' if self.llm.is_available else '❌ Disabled (set GOOGLE_API_KEY)'}")
            print(f"\nNext runs:\n{self._get_next_run_times()}")
            print("\n✓ Waiting for scheduled runs...")
            print("✓ Press Ctrl+C to stop\n")
            
            # Keep the scheduler running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        
        except Exception as e:
            print(f"❌ Error starting scheduler: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_next_run_times(self):
        """Get all next scheduled run times."""
        lines = []
        for job_id in ['daily_news', 'daily_summary', 'market_open_analysis']:
            job = self.scheduler.get_job(job_id)
            if job:
                next_time = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else "Unknown"
                lines.append(f"  {job.name}: {next_time}")
        return "\n".join(lines) if lines else "  No jobs scheduled"
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            print("\n" + "="*80)
            print("🛑 SCHEDULED TRADING BOT STOPPED")
            print("="*80 + "\n")
    
    def test_run(self):
        """Run analysis immediately (for testing)."""
        print("\n🧪 Testing scheduled analysis...\n")
        asyncio.run(self.run_analysis())
    
    def show_schedule(self):
        """Display the schedule."""
        print("\n" + "="*80)
        print("📅 TRADING BOT SCHEDULE")
        print("="*80)
        print("Frequency: Every weekday (Monday - Friday)")
        print()
        print("📰 8:00am EST - Daily Market News (LLM)")
        print("   → Posts news briefing in #daily-news")
        print()
        print("🌅 8:30am EST - Daily Summary & Predictions (LLM)")
        print("   → Scans all assets, posts summary in #daily-summary")
        print()
        print("📊 9:00am EST - Market Open Analysis")
        print("   → Full chart analysis, signals to timeframe channels")
        print()
        print(f"Assets: {', '.join(self.config.PRIMARY_TICKERS)}")
        print(f"Timeframes: {', '.join(self.config.TIMEFRAMES)}")
        print("="*80 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scheduled Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scheduler.py                 # Start scheduler
  python scheduler.py --test          # Test analysis now
  python scheduler.py --show-schedule # Show schedule
        """
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run analysis immediately (for testing)'
    )
    
    parser.add_argument(
        '--show-schedule',
        action='store_true',
        help='Display the schedule and exit'
    )
    
    args = parser.parse_args()
    
    # Create bot
    bot = ScheduledTradingBot()
    
    # Validate config
    is_valid, message = Config.validate()
    print(f"\n{message}")
    
    if not is_valid:
        print("\n❌ Configuration invalid - cannot start scheduler")
        return 1
    
    # Show schedule info
    Config.print_config()
    bot.show_schedule()
    
    # Handle commands
    if args.show_schedule:
        return 0
    
    if args.test:
        bot.test_run()
        return 0
    
    # Schedule and start
    bot.schedule_all()
    bot.start()
    
    return 0


if __name__ == "__main__":
    exit(main())
