"""
Discord Bot Commands
====================
Discord bot with commands to run trading analysis and send signals.
LLM-powered features: strategy suggestions, daily summaries, news, signal explanations.

Commands:
  !analyze all          - Run full multi-asset analysis
  !analyze TSLA         - Analyze specific ticker
  !strategy btc         - LLM strategy for an asset (posted in asset channel)
  !marketnews           - LLM market news summary
  !explain              - Explain the last signal or an indicator
  !status               - Show bot status
  !commands             - Show available commands
  !schedule             - Show scheduled run times

Usage:
  python discord_bot.py
"""

import discord
from discord.ext import commands, tasks
import asyncio
import sys
import os
import logging

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from src.llm_wrapper import LLMWrapper
from src.strategy import get_strategy_params
from datetime import datetime, time
import pytz

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger('discord_bot')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Global config
config = Config()

# LLM wrapper
llm = LLMWrapper(api_key=config.GOOGLE_API_KEY, model=config.LLM_MODEL)

# Strategy parameters
strategy_params = get_strategy_params()

# Store recent signals for !explain
recent_signals = {}

# Ticker mapping for aliases
TICKER_MAP = {
    'tsla': 'TSLA',
    'tesla': 'TSLA',
    'btc': 'BTC-USD',
    'bitcoin': 'BTC-USD',
    'aapl': 'AAPL',
    'apple': 'AAPL',
    'eth': 'ETH-USD',
    'ethereum': 'ETH-USD',
    'sp500': '^GSPC',
    'sp': '^GSPC',
    'snp': '^GSPC',
    'xrp': 'XRP-USD',
    'ripple': 'XRP-USD',
    'nvda': 'NVDA',
    'nvidia': 'NVDA',
    'gld': 'GLD',
    'gold': 'GLD',
    'slv': 'SLV',
    'silver': 'SLV',
}

# Timeframe emojis
TIMEFRAME_EMOJIS = {
    '1m': '⚡',
    '5m': '📊',
    '15m': '📈',
    '1h': '🕐',
}


def resolve_ticker(alias: str) -> str:
    """Resolve a ticker alias to its canonical form."""
    key = alias.lower().strip()
    return TICKER_MAP.get(key, alias.upper())


class AnalysisResult:
    """Holds analysis results."""
    def __init__(self):
        self.signals = {}
        self.total_signals = 0


# =========================================================================
# SCHEDULED TASKS (8:00am news, 8:30am summary, 9:00am analysis)
# =========================================================================

@tasks.loop(time=[time(hour=13, minute=0)])  # 8:00am EST = 13:00 UTC
async def daily_news_task():
    """Post daily market news at 8:00am EST."""
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Only run on weekdays
    if now.weekday() >= 5:
        return
    
    logger.info("Running scheduled daily news (8:00am EST)")
    
    try:
        news_text = await llm.generate_market_news(
            assets=config.PRIMARY_TICKERS,
            asset_names=config.TICKER_NAMES
        )
        
        channel = bot.get_channel(int(config.DAILY_NEWS_CHANNEL))
        if channel:
            embed = discord.Embed(
                title="📰 Daily Market News Briefing",
                description=news_text[:4096],
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Generated {now.strftime('%B %d, %Y')} • 8:00am EST")
            await channel.send(embed=embed)
            logger.info("Daily news posted successfully")
        else:
            logger.error(f"Daily news channel not found: {config.DAILY_NEWS_CHANNEL}")
            
    except Exception as e:
        logger.error(f"Error posting daily news: {e}")


@tasks.loop(time=[time(hour=13, minute=30)])  # 8:30am EST = 13:30 UTC
async def daily_summary_task():
    """Scan all assets and post LLM daily summary at 8:30am EST."""
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Only run on weekdays
    if now.weekday() >= 5:
        return
    
    logger.info("Running scheduled daily summary (8:30am EST) - scanning all assets first")
    
    try:
        # Step 1: Scan all assets
        analyzer = MultiTimeframeAnalyzer(config)
        scan_results = await analyzer.analyze_all()
        await analyzer.close()
        
        # Store signals for !explain
        for tf, signals in scan_results.items():
            for sig in signals:
                key = f"{sig['ticker']}_{sig['timeframe']}"
                recent_signals[key] = sig
        
        # Step 2: Generate LLM summary with predictions
        summary_text = await llm.generate_daily_summary(
            scan_results=scan_results,
            strategy_params=strategy_params
        )
        
        # Step 3: Post to daily-summary channel
        channel = bot.get_channel(int(config.DAILY_SUMMARY_CHANNEL))
        if channel:
            embed = discord.Embed(
                title="🌅 Pre-Market Daily Summary & Predictions",
                description=summary_text[:4096],
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            
            # Count signals
            total = sum(len(v) for v in scan_results.values())
            buys = sum(1 for v in scan_results.values() for s in v if s.get('signal') == 'BUY')
            sells = sum(1 for v in scan_results.values() for s in v if s.get('signal') == 'SELL')
            
            embed.add_field(
                name="📊 Scan Results",
                value=f"**{total}** signals detected ({buys} BUY / {sells} SELL)",
                inline=False
            )
            embed.set_footer(text=f"Market Open Summary • {now.strftime('%B %d, %Y')} • 8:30am EST")
            await channel.send(embed=embed)
            logger.info("Daily summary posted successfully")
        else:
            logger.error(f"Daily summary channel not found: {config.DAILY_SUMMARY_CHANNEL}")
            
    except Exception as e:
        logger.error(f"Error posting daily summary: {e}")
        import traceback
        traceback.print_exc()


@tasks.loop(time=[time(hour=14, minute=0)])  # 9:00am EST = 14:00 UTC
async def market_open_analysis_task():
    """Run full chart analysis at 9:00am EST market open."""
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Only run on weekdays
    if now.weekday() >= 5:
        return
    
    logger.info("Running scheduled market open analysis (9:00am EST)")
    
    try:
        analyzer = MultiTimeframeAnalyzer(config)
        scan_results = await analyzer.analyze_all()
        await analyzer.close()
        
        # Store signals for !explain
        for tf, signals in scan_results.items():
            for sig in signals:
                key = f"{sig['ticker']}_{sig['timeframe']}"
                recent_signals[key] = sig
        
        logger.info("Market open analysis complete")
        
    except Exception as e:
        logger.error(f"Error during market open analysis: {e}")
        import traceback
        traceback.print_exc()


# =========================================================================
# BOT EVENTS
# =========================================================================

@bot.event
async def on_ready():
    """Bot is ready - start scheduled tasks."""
    print(f"\n✅ Bot connected as {bot.user}")
    print(f"   Prefix: !")
    print(f"   LLM: {'✅ Enabled' if llm.is_available else '❌ Disabled (set GOOGLE_API_KEY)'}")
    print(f"   Watching for commands...\n")
    
    # Start scheduled tasks
    if not daily_news_task.is_running():
        daily_news_task.start()
        logger.info("Scheduled: Daily News at 8:00am EST")
    
    if not daily_summary_task.is_running():
        daily_summary_task.start()
        logger.info("Scheduled: Daily Summary at 8:30am EST")
    
    if not market_open_analysis_task.is_running():
        market_open_analysis_task.start()
        logger.info("Scheduled: Market Open Analysis at 9:00am EST")
    
    print("📅 Scheduled Tasks:")
    print("   📰 8:00am EST - Daily Market News → #daily-news")
    print("   🌅 8:30am EST - Daily Summary & Predictions → #daily-summary")
    print("   📊 9:00am EST - Full Chart Analysis → timeframe channels")
    print()


@bot.command(name='analyze', help='Analyze ticker(s): !analyze TSLA or !analyze all')
async def analyze(ctx, *, ticker: str = None):
    """Run analysis on specific ticker or all tickers."""
    
    if not ticker:
        embed = discord.Embed(
            title="❌ Missing Argument",
            description="Usage: `!analyze TSLA` or `!analyze all`",
            color=discord.Color.red()
        )
        embed.add_field(name="Available Tickers", value=", ".join(config.PRIMARY_TICKERS), inline=False)
        await ctx.send(embed=embed)
        return
    
    ticker = ticker.upper().strip()
    
    # Handle "all" command
    if ticker == 'ALL':
        tickers_to_analyze = config.PRIMARY_TICKERS
        analysis_type = "Full Market"
    else:
        # Try to map ticker alias
        ticker = resolve_ticker(ticker)
        
        # Validate ticker
        if ticker not in config.PRIMARY_TICKERS:
            embed = discord.Embed(
                title="❌ Invalid Ticker",
                description=f"`{ticker}` is not in the watchlist",
                color=discord.Color.red()
            )
            embed.add_field(name="Available Tickers", value=", ".join(config.PRIMARY_TICKERS), inline=False)
            await ctx.send(embed=embed)
            return
        
        tickers_to_analyze = [ticker]
        analysis_type = f"{config.get_ticker_display_name(ticker)}"
    
    # Send initial response
    embed = discord.Embed(
        title=f"🔄 Running Analysis",
        description=f"Analyzing {analysis_type}...",
        color=discord.Color.blue()
    )
    embed.add_field(name="Tickers", value=", ".join(tickers_to_analyze), inline=False)
    embed.add_field(name="Timeframes", value=", ".join(config.TIMEFRAMES), inline=False)
    status_message = await ctx.send(embed=embed)
    
    try:
        # Run analysis
        analyzer = MultiTimeframeAnalyzer(config)
        
        total_signals = 0
        results_by_tf = {tf: [] for tf in config.TIMEFRAMES}
        
        logger.info(f"[Discord Command] Analyzing: {', '.join(tickers_to_analyze)}")
        
        for ticker_to_analyze in tickers_to_analyze:
            for timeframe in config.TIMEFRAMES:
                signal_data = await analyzer.analyze_ticker_timeframe(ticker_to_analyze, timeframe)
                
                if signal_data:
                    results_by_tf[timeframe].append(signal_data)
                    total_signals += 1
                    
                    # Store for !explain
                    key = f"{signal_data['ticker']}_{signal_data['timeframe']}"
                    recent_signals[key] = signal_data
                    
                    # Send signal to Discord
                    await analyzer.process_signal(signal_data)
        
        # Create summary embed
        summary_embed = discord.Embed(
            title=f"✅ Analysis Complete",
            description=f"Analyzed {len(tickers_to_analyze)} ticker(s) across {len(config.TIMEFRAMES)} timeframes",
            color=discord.Color.green()
        )
        
        summary_embed.add_field(
            name="📈 Total Signals",
            value=f"**{total_signals}** signals generated",
            inline=False
        )
        
        # Add breakdown by timeframe
        breakdown = ""
        for tf in config.TIMEFRAMES:
            emoji = TIMEFRAME_EMOJIS.get(tf, '⏱️')
            count = len(results_by_tf[tf])
            breakdown += f"{emoji} **{tf.upper()}**: {count} signals\n"
        
        summary_embed.add_field(name="By Timeframe", value=breakdown or "No signals", inline=False)
        summary_embed.add_field(name="Posted To", value="Signals sent to their respective timeframe channels", inline=False)
        summary_embed.set_footer(text=f"Analysis completed at {datetime.now().strftime('%H:%M:%S')}")
        
        # Update status message
        await status_message.edit(embed=summary_embed)
        
        logger.info(f"Analysis complete: {total_signals} signals")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        
        error_embed = discord.Embed(
            title="❌ Analysis Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        try:
            await status_message.edit(embed=error_embed)
        except:
            await ctx.send(embed=error_embed)


# =========================================================================
# COMMAND: !strategy <asset>
# =========================================================================

@bot.command(name='strategy', help='Get LLM strategy for an asset: !strategy btc')
async def strategy_cmd(ctx, *, asset: str = None):
    """Generate an LLM strategy suggestion for a specific asset."""
    
    if not asset:
        embed = discord.Embed(
            title="❌ Missing Asset",
            description="Usage: `!strategy btc` or `!strategy TSLA`",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Available Assets",
            value="\n".join([f"`{k}` → {v}" for k, v in TICKER_MAP.items() if k in ['btc', 'eth', 'xrp', 'tsla', 'aapl', 'nvda', 'gold', 'silver', 'sp500']]),
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Resolve ticker
    ticker = resolve_ticker(asset)
    
    if ticker not in config.PRIMARY_TICKERS:
        embed = discord.Embed(
            title="❌ Invalid Asset",
            description=f"`{asset}` is not in the watchlist",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    ticker_display = config.get_ticker_display_name(ticker)
    
    # Check LLM availability
    if not llm.is_available:
        embed = discord.Embed(
            title="⚠️ LLM Not Available",
            description="Set `GOOGLE_API_KEY` in your `.env` file to enable AI strategy suggestions.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # Send "thinking" message
    thinking_embed = discord.Embed(
        title=f"🧠 Generating Strategy for {ticker_display}",
        description="Scanning market data and generating AI strategy...",
        color=discord.Color.blue()
    )
    status_msg = await ctx.send(embed=thinking_embed)
    
    try:
        # Step 1: Scan this asset across all timeframes
        analyzer = MultiTimeframeAnalyzer(config)
        market_data = {}
        
        for timeframe in config.TIMEFRAMES:
            signal_data = await analyzer.analyze_ticker_timeframe(ticker, timeframe)
            if signal_data:
                market_data[timeframe] = signal_data
                # Store for !explain
                key = f"{ticker}_{timeframe}"
                recent_signals[key] = signal_data
        
        await analyzer.close()
        
        # Step 2: Generate LLM strategy
        strategy_text = await llm.generate_strategy(
            ticker=ticker,
            ticker_display=ticker_display,
            market_data=market_data,
            strategy_params=strategy_params,
            risk_profile="moderate"
        )
        
        # Step 3: Post in the asset's channel
        asset_channel_id = config.get_channel_for_asset(ticker)
        
        strategy_embed = discord.Embed(
            title=f"🎯 Strategy: {ticker_display}",
            description=strategy_text[:4096],
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        
        # Add indicator snapshot
        if market_data:
            snapshot = ""
            for tf, data in market_data.items():
                emoji = TIMEFRAME_EMOJIS.get(tf, '⏱️')
                sig_emoji = "🟢" if data.get('signal') == 'BUY' else "🔴"
                snapshot += f"{emoji} **{tf}**: {sig_emoji} {data.get('signal', 'HOLD')} ({data.get('confidence', 0)*100:.0f}%)\n"
            strategy_embed.add_field(name="📊 Current Signals", value=snapshot or "No active signals", inline=False)
        
        strategy_embed.set_footer(text=f"Strategy for {ticker} • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Send to asset channel if available, otherwise reply in current channel
        if asset_channel_id:
            asset_channel = bot.get_channel(int(asset_channel_id))
            if asset_channel:
                await asset_channel.send(embed=strategy_embed)
                # Update the status message
                done_embed = discord.Embed(
                    title=f"✅ Strategy Generated for {ticker_display}",
                    description=f"Strategy posted in <#{asset_channel_id}>",
                    color=discord.Color.green()
                )
                await status_msg.edit(embed=done_embed)
            else:
                await status_msg.edit(embed=strategy_embed)
        else:
            await status_msg.edit(embed=strategy_embed)
        
        logger.info(f"Strategy generated for {ticker}")
        
    except Exception as e:
        logger.error(f"Error generating strategy: {e}")
        import traceback
        traceback.print_exc()
        
        error_embed = discord.Embed(
            title="❌ Strategy Generation Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await status_msg.edit(embed=error_embed)


# =========================================================================
# COMMAND: !marketnews
# =========================================================================

@bot.command(name='marketnews', help='Get LLM market news summary')
async def marketnews(ctx):
    """Generate and post a market news summary."""
    
    if not llm.is_available:
        embed = discord.Embed(
            title="⚠️ LLM Not Available",
            description="Set `GOOGLE_API_KEY` in your `.env` file to enable AI news summaries.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # Send "thinking" message
    thinking_embed = discord.Embed(
        title="📰 Fetching Market News...",
        description="Generating AI market news summary...",
        color=discord.Color.blue()
    )
    status_msg = await ctx.send(embed=thinking_embed)
    
    try:
        news_text = await llm.generate_market_news(
            assets=config.PRIMARY_TICKERS,
            asset_names=config.TICKER_NAMES
        )
        
        news_embed = discord.Embed(
            title="📰 Market News Summary",
            description=news_text[:4096],
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        news_embed.set_footer(text=f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} EST")
        
        # Post in daily-news channel
        news_channel = bot.get_channel(int(config.DAILY_NEWS_CHANNEL))
        if news_channel:
            await news_channel.send(embed=news_embed)
            done_embed = discord.Embed(
                title="✅ Market News Posted",
                description=f"News summary posted in <#{config.DAILY_NEWS_CHANNEL}>",
                color=discord.Color.green()
            )
            await status_msg.edit(embed=done_embed)
        else:
            await status_msg.edit(embed=news_embed)
        
        logger.info("Market news generated")
        
    except Exception as e:
        logger.error(f"Error generating market news: {e}")
        error_embed = discord.Embed(
            title="❌ News Generation Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await status_msg.edit(embed=error_embed)


# =========================================================================
# COMMAND: !explain
# =========================================================================

@bot.command(name='explain', help='Explain a signal or indicator: !explain btc 5m or !explain alligator')
async def explain(ctx, *, query: str = None):
    """Explain a signal or trading concept."""
    
    if not llm.is_available:
        embed = discord.Embed(
            title="⚠️ LLM Not Available",
            description="Set `GOOGLE_API_KEY` in your `.env` file to enable AI explanations.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    if not query:
        embed = discord.Embed(
            title="📚 Signal Explanation",
            description="Usage:\n`!explain btc 5m` - Explain last signal for BTC on 5m\n`!explain alligator` - What is the Alligator indicator?\n`!explain stochastic` - What is the Stochastic Oscillator?",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    # Send "thinking" message
    thinking_embed = discord.Embed(
        title="🧠 Generating Explanation...",
        color=discord.Color.blue()
    )
    status_msg = await ctx.send(embed=thinking_embed)
    
    try:
        parts = query.lower().strip().split()
        
        # Check if user is asking about a specific signal (e.g., "btc 5m")
        signal_found = False
        if len(parts) >= 2:
            ticker = resolve_ticker(parts[0])
            timeframe = parts[1]
            key = f"{ticker}_{timeframe}"
            
            if key in recent_signals:
                signal_data = recent_signals[key]
                explanation = await llm.explain_signal(signal_data, strategy_params)
                
                explain_embed = discord.Embed(
                    title=f"📚 Signal Explanation: {config.get_ticker_display_name(ticker)} ({timeframe})",
                    description=explanation[:4096],
                    color=discord.Color.teal(),
                    timestamp=datetime.utcnow()
                )
                await status_msg.edit(embed=explain_embed)
                signal_found = True
        
        if not signal_found:
            # Treat as an education question
            answer = await llm.answer_education_question(query)
            
            explain_embed = discord.Embed(
                title=f"📚 Trading Education",
                description=answer[:4096],
                color=discord.Color.teal(),
                timestamp=datetime.utcnow()
            )
            await status_msg.edit(embed=explain_embed)
        
        logger.info(f"Explanation generated for: {query}")
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        error_embed = discord.Embed(
            title="❌ Explanation Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await status_msg.edit(embed=error_embed)


# =========================================================================
# COMMAND: !status
# =========================================================================

@bot.command(name='status', help='Show bot status')
async def status(ctx):
    """Show bot status and configuration."""
    tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(tz)
    
    embed = discord.Embed(
        title="🤖 Trading Bot Status",
        description="Live and monitoring markets",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="📊 Assets Monitored",
        value="\n".join([f"• {config.get_ticker_display_name(t)}" for t in config.PRIMARY_TICKERS]),
        inline=True
    )
    
    embed.add_field(
        name="⏱️ Timeframes",
        value=", ".join(config.TIMEFRAMES),
        inline=True
    )
    
    embed.add_field(
        name="📅 Scheduled Runs",
        value=(
            "📰 8:00am EST - Daily News\n"
            "🌅 8:30am EST - Daily Summary\n"
            "📊 9:00am EST - Chart Analysis"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🧠 LLM Status",
        value=f"{'✅ Enabled' if llm.is_available else '❌ Disabled (set GOOGLE_API_KEY)'}",
        inline=True
    )
    
    embed.add_field(
        name="🕐 Current Time",
        value=f"{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        inline=True
    )
    
    embed.add_field(
        name="💻 System",
        value=f"Data: {config.DATA_PROVIDER} | Model: {config.LLM_MODEL} | Debug: {config.DEBUG}",
        inline=False
    )
    
    embed.set_footer(text="Use !commands for available commands")
    
    await ctx.send(embed=embed)


# =========================================================================
# COMMAND: !schedule
# =========================================================================

@bot.command(name='schedule', help='Show scheduled run times')
async def schedule(ctx):
    """Show when the bot runs automatically."""
    embed = discord.Embed(
        title="📅 Trading Bot Schedule",
        description="Automatic daily schedule (weekdays only)",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📰 8:00am EST - Daily Market News",
        value="LLM-generated news briefing → <#" + config.DAILY_NEWS_CHANNEL + ">",
        inline=False
    )
    
    embed.add_field(
        name="🌅 8:30am EST - Daily Summary & Predictions",
        value="Scans all assets, then LLM generates predictions → <#" + config.DAILY_SUMMARY_CHANNEL + ">",
        inline=False
    )
    
    embed.add_field(
        name="📊 9:00am EST - Full Chart Analysis",
        value="Full analysis of all 9 assets on 4 timeframes → timeframe channels",
        inline=False
    )
    
    embed.add_field(
        name="📢 Asset Channels",
        value="\n".join([f"• {config.get_ticker_display_name(t)}: <#{config.get_channel_for_asset(t)}>" for t in config.PRIMARY_TICKERS if config.get_channel_for_asset(t)]),
        inline=False
    )
    
    embed.add_field(
        name="💡 On-Demand Commands",
        value="`!analyze TICKER` • `!strategy TICKER` • `!marketnews` • `!explain`",
        inline=False
    )
    
    await ctx.send(embed=embed)


# =========================================================================
# COMMAND: !tickers
# =========================================================================

@bot.command(name='tickers', help='Show monitored assets')
async def tickers(ctx):
    """Show all monitored tickers."""
    embed = discord.Embed(
        title="📊 Monitored Assets",
        color=discord.Color.blue()
    )
    
    ticker_list = ""
    for ticker in config.PRIMARY_TICKERS:
        display_name = config.get_ticker_display_name(ticker)
        channel_id = config.get_channel_for_asset(ticker)
        channel_ref = f" → <#{channel_id}>" if channel_id else ""
        ticker_list += f"{display_name} (`{ticker}`){channel_ref}\n"
    
    embed.add_field(name="Assets", value=ticker_list, inline=False)
    
    embed.add_field(
        name="Quick Commands",
        value="`!analyze TSLA`\n`!strategy btc`\n`!analyze all`",
        inline=False
    )
    
    await ctx.send(embed=embed)


# =========================================================================
# COMMAND: !commands
# =========================================================================

@bot.command(name='commands', help='Show available commands')
async def commands_command(ctx):
    """Show available bot commands."""
    embed = discord.Embed(
        title="🤖 Trading Bot Commands",
        description="All available commands",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 Analysis",
        value=(
            "`!analyze <ticker>` - Analyze specific asset\n"
            "`!analyze all` - Full market analysis (9 assets × 4 timeframes)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🧠 AI-Powered (LLM)",
        value=(
            "`!strategy <asset>` - AI strategy for an asset (posted in asset channel)\n"
            "`!marketnews` - AI market news summary\n"
            "`!explain <asset> <tf>` - Explain a signal (e.g., `!explain btc 5m`)\n"
            "`!explain <topic>` - Learn about an indicator or concept"
        ),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Info",
        value=(
            "`!status` - Bot status and configuration\n"
            "`!tickers` - List all monitored assets\n"
            "`!schedule` - Show scheduled run times\n"
            "`!commands` - This help message"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📋 Ticker Aliases",
        value="btc, eth, xrp, tsla, tesla, aapl, apple, nvda, nvidia, gold, silver, sp500",
        inline=False
    )
    
    embed.add_field(
        name="📅 Automatic Schedule",
        value=(
            "📰 8:00am - Daily News\n"
            "🌅 8:30am - Summary & Predictions\n"
            "📊 9:00am - Chart Analysis"
        ),
        inline=False
    )
    
    embed.set_footer(text="All times are EST (US/Eastern)")
    
    await ctx.send(embed=embed)


# =========================================================================
# ERROR HANDLING
# =========================================================================

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"Unknown command. Use `!commands` for available commands.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Arguments",
            description=f"Use `!commands` for command syntax",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ Error: {str(error)}")


# =========================================================================
# MAIN
# =========================================================================

def main():
    """Main entry point."""
    # Fix Windows console encoding for emoji/unicode
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Validate config
    is_valid, message = Config.validate()
    print(f"\n{message}")
    
    if not is_valid:
        print("\n❌ Configuration invalid")
        return 1
    
    # Show config
    Config.print_config()
    
    # Get token
    token = config.DISCORD_BOT_TOKEN
    if not token:
        print("❌ DISCORD_BOT_TOKEN not set in .env")
        return 1
    
    print("\n" + "="*80)
    print("🤖 DISCORD BOT - LLM-ENHANCED TRADING ASSISTANT")
    print("="*80)
    print("\n📊 Analysis Commands:")
    print("  !analyze <ticker>       - Analyze specific asset")
    print("  !analyze all            - Full market analysis")
    print("\n🧠 AI Commands:")
    print("  !strategy <asset>       - AI strategy suggestion")
    print("  !marketnews             - AI market news summary")
    print("  !explain <asset> <tf>   - Explain a signal")
    print("  !explain <topic>        - Learn about indicators")
    print("\nℹ️  Info Commands:")
    print("  !status                 - Bot status")
    print("  !tickers                - Monitored assets")
    print("  !schedule               - Show schedule")
    print("  !commands               - All commands")
    print("\n📅 Scheduled Tasks:")
    print("  📰 8:00am EST  - Daily Market News")
    print("  🌅 8:30am EST  - Daily Summary (scan + LLM predictions)")
    print("  📊 9:00am EST  - Full Chart Analysis")
    print(f"\n🧠 LLM: {'✅ Enabled (' + config.LLM_MODEL + ')' if config.LLM_ENABLED else '❌ Disabled (set GOOGLE_API_KEY)'}")
    print("="*80 + "\n")
    
    # Start bot
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
