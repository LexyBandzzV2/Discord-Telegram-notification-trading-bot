"""
LLM Wrapper Module
==================
Handles all LLM (Google Gemini) interactions for the trading bot:
- Daily market summaries with predictions
- Asset-specific strategy suggestions
- Market news summaries
- Signal explanations and education

Usage:
    llm = LLMWrapper(api_key="your_key")
    summary = await llm.generate_daily_summary(scan_results)
    strategy = await llm.generate_strategy(ticker, market_data, strategy_params)
"""

import asyncio
import json
import logging
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger('llm_wrapper')

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class LLMWrapper:
    """
    Wrapper for Google Gemini REST API to generate trading insights,
    strategies, news summaries, and signal explanations.
    Uses aiohttp directly (no SDK needed).
    """
    
    def __init__(self, api_key: str, model: str = 'gemini-2.5-flash'):
        """
        Initialize LLM wrapper.
        
        Args:
            api_key: Google API key
            model: Model to use (default: gemini-2.0-flash)
        """
        self.api_key = api_key
        self.model = model
        self._available = bool(api_key)
        
        if not api_key:
            logger.warning("No Google API key provided - LLM features disabled")
        else:
            logger.info(f"LLM wrapper initialized with model: {model}")
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self._available
    
    async def _chat(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """
        Mocked _chat method to simulate LLM API response.
        """
        logger.info("Mocking LLM API response.")
        return "This is a mocked response for testing purposes."
    
    # =========================================================================
    # DAILY SUMMARY (8:30am EST - after scanning all assets)
    # =========================================================================
    
    async def generate_daily_summary(self, scan_results: Dict[str, Any],
                                      strategy_params: Dict[str, Any]) -> str:
        """
        Generate a daily trading summary with market predictions.
        Called after scanning all assets at 8:30am EST before market open.
        
        Args:
            scan_results: Results from scanning all assets across timeframes
            strategy_params: Trading strategy parameters
            
        Returns:
            LLM-generated daily summary text
        """
        system_prompt = """You are a friendly trading analyst writing a pre-market daily summary for regular people who are learning to trade.

Your job is to take the scanned indicator data and explain it clearly so anyone can understand.

For EACH asset that has a signal, include:
- The asset name and current price
- What the Alligator indicator is showing (e.g. "The jaw, teeth, and lips are spreading apart which means a strong trend is forming" or "They're tangled up which means the market is choppy")
- What Stochastic is showing (e.g. "Stochastic K is at 82 which is in overbought territory - the price has been running hot" or "K crossed above D at 25 which is a bullish crossover from oversold")
- What Vortex is showing (e.g. "VI+ is above VI- which confirms bullish momentum" or "VI- just crossed above VI+ signaling bearish pressure")
- A simple prediction: where you think this asset moves at market open and WHY based on the indicators
- Confidence level in plain English ("Strong signal - all 3 indicators agree" vs "Mixed signals - only 2 of 3 align")

Also include:
- A "Top Picks" section highlighting the 2-3 strongest setups
- Key risk factors for the day

Use emojis, bold text, and bullet points for Discord formatting.
Write like you're explaining to a friend, not a textbook.
Max 3500 characters.
Always end with a short risk disclaimer."""

        # Build market data context
        market_context = self._format_scan_results(scan_results)
        strategy_context = self._format_strategy_params(strategy_params)
        
        user_prompt = f"""Generate a detailed pre-market daily trading summary for {datetime.now().strftime('%A, %B %d, %Y')}.

**Scanned Market Data (from our bot's live scan):**
{market_context}

**Our Trading Strategy uses these 3 indicators:**
{strategy_context}

Go through each asset that has signals. For each one, explain what the 3 indicators are telling us in plain English and give a prediction for market open. Then highlight the top 2-3 strongest setups of the day."""

        return await self._chat(system_prompt, user_prompt, max_tokens=2000)
    
    # =========================================================================
    # STRATEGY SUGGESTIONS (!strategy <asset>)
    # =========================================================================
    
    async def generate_strategy(self, ticker: str, ticker_display: str,
                                 market_data: Dict[str, Any],
                                 strategy_params: Dict[str, Any],
                                 risk_profile: str = "moderate") -> str:
        """
        Generate a strategy suggestion for a specific asset.
        
        Args:
            ticker: Asset ticker (e.g., 'BTC-USD')
            ticker_display: Display name (e.g., '₿ Bitcoin')
            market_data: Current market data and indicators for this asset
            strategy_params: Trading strategy parameters
            risk_profile: User risk profile (conservative, moderate, aggressive)
            
        Returns:
            LLM-generated strategy summary
        """
        system_prompt = f"""You are a trading strategist providing actionable insights for {ticker_display}.

Your task is to analyze the current market data and provide a concise, technical trading strategy based on the following indicators:

1. **Alligator**: Explain the trend direction and momentum based on the positions of the jaw, teeth, and lips. Are they spreading apart (trending) or tangled (choppy)?

2. **Stochastic Oscillator**: Analyze the %K and %D values. Are they in overbought, oversold, or neutral zones? Have any crossovers occurred?

3. **Vortex Indicator**: Determine the dominant trend direction based on the positions of VI+ and VI-. Are they indicating an uptrend or downtrend?

Provide the following:
- **Market Analysis**: A brief summary of the current market conditions for this asset.
- **Next Steps**: What should the trader do next? (e.g., Buy, Sell, or Wait) and why.
- **Key Levels**: Highlight important support and resistance levels.
- **Risk Factors**: Mention any risks or uncertainties to watch out for.

Use clear, concise language and focus on actionable insights. Avoid unnecessary details. Max 2000 characters."""

        market_context = self._format_asset_data(ticker, market_data)
        strategy_context = self._format_strategy_params(strategy_params)
        
        user_prompt = f"""Generate a concise trading strategy for {ticker_display} ({ticker}).

**Live Indicator Readings:**
{market_context}

**Strategy Parameters:**
{strategy_context}

Focus on technical analysis using the Alligator, Stochastic, and Vortex indicators. Provide actionable next steps for the trader based on the chart analysis."""

        return await self._chat(system_prompt, user_prompt, max_tokens=1500)
    
    # =========================================================================
    # MARKET NEWS (!marketnews)
    # =========================================================================
    
    async def generate_market_news(self, assets: List[str],
                                    asset_names: Dict[str, str]) -> str:
        """
        Generate a market news summary.
        
        Args:
            assets: List of tracked asset tickers
            asset_names: Mapping of ticker to display name
            
        Returns:
            LLM-generated news summary
        """
        system_prompt = """You are a friendly financial news reporter writing a daily market briefing for regular people.

Provide:
1. **Big Picture** - What's the overall market mood today? (bullish, bearish, uncertain) and WHY in simple terms
2. **Top Headlines** - 3-5 most important market-moving news stories. For each, explain WHY it matters and which assets it affects
3. **Economic Calendar** - Any data releases today (jobs report, CPI, Fed meetings, etc.) and what they could do to prices
4. **Asset Spotlight** - Quick notes on any of our tracked assets that have big news (earnings, upgrades, regulatory news, etc.)
5. **Watch Out For** - Upcoming events this week that could cause big moves

Write like a news anchor explaining to regular viewers, not Wall Street jargon.
Use emojis, bold, bullets for Discord formatting.
Max 3500 characters."""

        asset_list = "\n".join([f"- {asset_names.get(t, t)} ({t})" for t in assets])
        
        user_prompt = f"""Generate a daily market news briefing for {datetime.now().strftime('%A, %B %d, %Y')}.

**Assets We Track:**
{asset_list}

Provide the most relevant news and upcoming events that could impact these assets today."""

        return await self._chat(system_prompt, user_prompt, max_tokens=2000)
    
    # =========================================================================
    # SIGNAL EXPLANATION (!explain & inline explanations)
    # =========================================================================
    
    async def explain_signal(self, signal_data: Dict[str, Any],
                              strategy_params: Dict[str, Any]) -> str:
        """
        Generate a detailed explanation for a specific signal.
        
        Args:
            signal_data: Signal data including indicators and confidence
            strategy_params: Trading strategy parameters
            
        Returns:
            LLM-generated signal explanation
        """
        system_prompt = """You are a patient trading teacher explaining why a specific signal was generated. Imagine you're explaining to someone who just started learning about trading.

For this signal, break down:
1. **Alligator**: What are the jaw, teeth, and lips doing? Are they opening up or closing? What does that tell us about the trend? Use a simple analogy.
2. **Stochastic**: What are the K and D numbers? Is the asset overbought or oversold? Did they cross? What does that mean in plain English?
3. **Vortex**: Is VI+ winning or VI-? What does that say about who's in control - buyers or sellers?
4. **Why the signal fired**: How did these 3 indicators line up to trigger a BUY or SELL? How many agreed?
5. **Confidence explained**: What does the confidence % mean? (e.g. 77% = 2-3 indicators agree)
6. **What to watch next**: What would confirm or invalidate this signal?
7. **Risk**: What's the main danger if this signal is wrong?

Format for Discord (emojis, bold, bullets). Write like you're texting a friend.
Max 2000 characters."""

        signal_context = self._format_signal_data(signal_data)
        strategy_context = self._format_strategy_params(strategy_params)
        
        user_prompt = f"""Explain this trading signal:

**Signal Data:**
{signal_context}

**Strategy Parameters:**
{strategy_context}

Explain why this signal was generated, what each indicator is telling us, and what the trader should consider."""

        return await self._chat(system_prompt, user_prompt, max_tokens=1200)
    
    async def generate_brief_explanation(self, signal_data: Dict[str, Any]) -> str:
        """
        Generate a brief 1-2 sentence explanation for inline signal messages.
        
        Args:
            signal_data: Signal data
            
        Returns:
            Brief explanation string
        """
        system_prompt = """You are a concise trading analyst. Provide a 1-2 sentence explanation of why this signal was generated, referencing the specific indicators. Max 200 characters."""

        signal_context = self._format_signal_data(signal_data)
        
        user_prompt = f"Briefly explain this signal:\n{signal_context}"
        
        return await self._chat(system_prompt, user_prompt, max_tokens=150)
    
    async def answer_education_question(self, question: str) -> str:
        """
        Answer trading education questions.
        
        Args:
            question: User's question about indicators, signals, etc.
            
        Returns:
            Educational answer
        """
        system_prompt = """You are a friendly trading teacher. Answer questions about trading concepts, indicators, and strategies in simple language that a beginner can understand.

Topics you cover:
- Technical indicators (Alligator, Stochastic, Vortex, RSI, MACD, etc.) - explain what they measure, how to read them, and when they're useful
- Trading signals - what BUY/SELL signals mean, how confidence works
- Risk management - stop losses, position sizing, risk/reward ratios
- Market structure - support/resistance, trends, breakouts
- General trading concepts - candlesticks, timeframes, volume

Always use real examples and analogies. If someone asks about an indicator, explain:
- What it does (in one simple sentence)
- How to read it (what the numbers/lines mean)
- When it's useful vs when it fails
- How our bot uses it

Format for Discord (emojis, bold, bullets). Keep it educational and encouraging.
Max 2000 characters."""

        return await self._chat(system_prompt, question, max_tokens=1200)
    
    # =========================================================================
    # HELPER METHODS - Format data for LLM prompts
    # =========================================================================
    
    def _format_scan_results(self, scan_results: Dict[str, Any]) -> str:
        """Format scan results into readable text for LLM prompt."""
        if not scan_results:
            return "No scan data available."
        
        lines = []
        for timeframe, signals in scan_results.items():
            if signals:
                lines.append(f"\n**{timeframe.upper()} Timeframe:**")
                for sig in signals:
                    ticker = sig.get('ticker', 'Unknown')
                    signal = sig.get('signal', 'N/A')
                    price = sig.get('price', 0)
                    confidence = sig.get('confidence', 0)
                    
                    emoji = "🟢" if signal == 'BUY' else "🔴"
                    lines.append(f"  {emoji} {ticker}: {signal} @ ${price:.2f} (Confidence: {confidence*100:.0f}%)")
                    
                    # Add indicator details if available
                    indicators = sig.get('indicators', {})
                    if indicators:
                        if 'stoch_status' in indicators:
                            lines.append(f"    Stoch: {indicators['stoch_status']}")
                        if 'alligator_status' in indicators:
                            lines.append(f"    Alligator: {indicators['alligator_status']}")
                        if 'vortex_status' in indicators:
                            lines.append(f"    Vortex: {indicators['vortex_status']}")
            else:
                lines.append(f"\n**{timeframe.upper()}:** No signals detected")
        
        return "\n".join(lines) if lines else "No market data available."
    
    def _format_asset_data(self, ticker: str, market_data: Dict[str, Any]) -> str:
        """Format asset-specific market data for LLM prompt."""
        if not market_data:
            return f"No data available for {ticker}."
        
        lines = [f"**Asset:** {ticker}"]
        
        for timeframe, data in market_data.items():
            if data:
                lines.append(f"\n  **{timeframe.upper()}:**")
                signal = data.get('signal', 'HOLD')
                price = data.get('price', 0)
                confidence = data.get('confidence', 0)
                lines.append(f"    Signal: {signal} | Price: ${price:.2f} | Confidence: {confidence*100:.0f}%")
                
                indicators = data.get('indicators', {})
                if indicators:
                    if 'stoch_k' in indicators:
                        lines.append(f"    Stoch K: {indicators['stoch_k']:.1f}, D: {indicators['stoch_d']:.1f}")
                    if 'alligator_status' in indicators:
                        lines.append(f"    Alligator: {indicators['alligator_status']}")
                    if 'vortex_status' in indicators:
                        lines.append(f"    Vortex: {indicators['vortex_status']}")
        
        return "\n".join(lines)
    
    def _format_strategy_params(self, strategy_params: Dict[str, Any]) -> str:
        """Format strategy parameters for LLM prompt."""
        if not strategy_params:
            return "No strategy parameters available."
        
        lines = []
        
        name = strategy_params.get('name', 'Custom Strategy')
        lines.append(f"**Strategy:** {name}")
        
        indicators = strategy_params.get('indicators', {})
        if indicators:
            lines.append("\n**Indicator Parameters:**")
            for ind_name, params in indicators.items():
                lines.append(f"  {ind_name}:")
                if isinstance(params, dict):
                    for k, v in params.items():
                        lines.append(f"    - {k}: {v}")
                else:
                    lines.append(f"    {params}")
        
        rules = strategy_params.get('entry_rules', [])
        if rules:
            lines.append("\n**Entry Rules:**")
            for rule in rules:
                lines.append(f"  • {rule}")
        
        risk = strategy_params.get('risk_management', {})
        if risk:
            lines.append("\n**Risk Management:**")
            for k, v in risk.items():
                lines.append(f"  • {k}: {v}")
        
        return "\n".join(lines)
    
    def _format_signal_data(self, signal_data: Dict[str, Any]) -> str:
        """Format signal data for LLM prompt."""
        if not signal_data:
            return "No signal data available."
        
        lines = []
        lines.append(f"**Asset:** {signal_data.get('ticker', 'Unknown')}")
        lines.append(f"**Signal:** {signal_data.get('signal', 'N/A')}")
        lines.append(f"**Timeframe:** {signal_data.get('timeframe', 'N/A')}")
        lines.append(f"**Price:** ${signal_data.get('price', 0):.2f}")
        lines.append(f"**Confidence:** {signal_data.get('confidence', 0)*100:.0f}%")
        
        indicators = signal_data.get('indicators', {})
        if indicators:
            lines.append("\n**Indicators:**")
            if 'stoch_k' in indicators:
                lines.append(f"  Stoch RSI: K={indicators['stoch_k']:.1f}, D={indicators['stoch_d']:.1f}")
                lines.append(f"  Stoch Status: {indicators.get('stoch_status', 'N/A')}")
            if 'alligator_status' in indicators:
                lines.append(f"  Alligator: {indicators['alligator_status']}")
            if 'vortex_status' in indicators:
                lines.append(f"  Vortex: {indicators['vortex_status']}")
        
        return "\n".join(lines)
