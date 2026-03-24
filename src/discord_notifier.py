"""
Discord Notification Module - Multi-Timeframe Edition
======================================================
Handles sending trade signals to Discord channels based on timeframes.
Each timeframe (1m, 3m, 5m, 15m, 1h) gets its own dedicated channel.

Usage:
    notifier = DiscordNotifier(bot_token="your_token", channels={...})
    notifier.send_buy_signal(ticker='TSLA', price=250.50, timeframe='5m', confidence=0.85)
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class SignalType(Enum):
    """Types of trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    ALERT = "ALERT"
    ERROR = "ERROR"


class DiscordNotifier:
    """
    Handles Discord notifications for trading signals.
    Routes signals to specific channels based on timeframe.
    """
    
    # Color codes for Discord embeds
    COLORS = {
        'BUY': 0x00FF00,        # Green
        'SELL': 0xFF0000,       # Red
        'ALERT': 0xFFFF00,      # Yellow
        'ERROR': 0xFF6600,      # Orange
    }
    
    # Timeframe emojis
    TIMEFRAME_EMOJIS = {
        '1m': '⚡',
        '3m': '🔥',
        '5m': '📊',
        '15m': '📈',
        '1h': '🕐',
    }
    
    def __init__(self, bot_token: str, channels: Dict[str, str]):
        """
        Initialize Discord notifier.
        
        Args:
            bot_token: Discord bot token
            channels: Dictionary mapping timeframes to channel IDs
                     e.g., {'1m': '123456789', '5m': '987654321'}
        """
        self.bot_token = bot_token
        self.channels = channels
        self.session = None
        
        if not bot_token:
            raise ValueError("bot_token must be provided")
        if not channels:
            raise ValueError("channels dictionary must be provided")
    
    async def _ensure_session(self):
        """Ensure aiohttp session is initialized."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def send_to_channel(self, channel_id: str, embed_data: Dict[str, Any]) -> bool:
        """
        Send message to a specific Discord channel.
        
        Args:
            channel_id: Discord channel ID
            embed_data: Dictionary with Discord embed data
            
        Returns:
            True if successful, False otherwise
        """
        if not channel_id:
            print("❌ Channel ID not provided")
            return False
        
        try:
            await self._ensure_session()
            
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            headers = {
                "Authorization": f"Bot {self.bot_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "embeds": [embed_data],
                "username": "Trading Bot"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    print(f"✓ Message sent to Discord (Channel: {channel_id}, Status: {response.status})")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to send Discord message (Status: {response.status}): {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error sending Discord message: {e}")
            return False
    
    def _format_detailed_indicators(self, indicators: Optional[Dict[str, Any]], 
                                    signal_type: SignalType) -> str:
        """
        Format detailed indicator information for Discord signals.
        Shows Stoch RSI, Alligator, and Vortex status.
        
        Args:
            indicators: Dictionary containing indicator data
            signal_type: BUY or SELL signal type
            
        Returns:
            Formatted indicator string for Discord
        """
        if not indicators:
            return ""
        
        formatted_parts = []
        
        # Price
        if 'price' in indicators:
            formatted_parts.append(f"**Price:** ${indicators['price']:.2f}")
        
        # Stochastic RSI Details
        if 'stoch_k' in indicators and 'stoch_d' in indicators:
            stoch_k = indicators['stoch_k']
            stoch_d = indicators['stoch_d']
            
            if stoch_k >= 80 or stoch_d >= 80:
                formatted_parts.append(f"**Stoch:** Overbought (≥80)")
            elif stoch_k <= 20 or stoch_d <= 20:
                formatted_parts.append(f"**Stoch:** Oversold (≤20)")
            else:
                formatted_parts.append(f"**Stoch:** Neutral")
        
        # Alligator - Show crossing and direction
        if 'alligator_status' in indicators:
            alligator_status = indicators['alligator_status']
            formatted_parts.append(f"**Alligator:** {alligator_status}")
        
        # Vortex - Show crossing status (simplified)
        if 'vortex_status' in indicators:
            vortex_status = indicators['vortex_status']
            # Simplify vortex text
            if signal_type == SignalType.BUY or 'Green cross' in vortex_status:
                formatted_parts.append("**Vortex:** Bullish cross (VI+ > VI-)")
            elif signal_type == SignalType.SELL or 'Red cross' in vortex_status:
                formatted_parts.append("**Vortex:** Bearish cross (VI- > VI+)")
            else:
                formatted_parts.append(f"**Vortex:** {vortex_status}")
        
        return "\n".join(formatted_parts)
    
    def _create_embed(self, signal_type: SignalType, 
                      ticker: str, ticker_display: str, price: float, 
                      timeframe: str, confidence: float, 
                      indicators: Optional[Dict[str, Any]] = None,
                      description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Discord embed for a trading signal.
        
        Args:
            signal_type: Type of signal (BUY, SELL, ALERT, ERROR)
            ticker: Stock ticker symbol (e.g., 'TSLA')
            ticker_display: Display name (e.g., '🚗 Tesla')
            price: Current price
            timeframe: Timeframe (e.g., '5m')
            confidence: Signal confidence (0-1)
            indicators: Dictionary of indicator values
            description: Additional description
            
        Returns:
            Dictionary representing Discord embed
        """
        tf_emoji = self.TIMEFRAME_EMOJIS.get(timeframe, '⏱️')
        signal_emoji = '🟢' if signal_type == SignalType.BUY else '🔴'
        
        embed = {
            "title": f"{signal_emoji} {signal_type.value} SIGNAL: {ticker_display}",
            "description": description or f"A {signal_type.value} signal has been detected on the {timeframe} chart",
            "color": self.COLORS.get(signal_type.value, 0xFFFFFF),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "fields": [
                {
                    "name": "💰 Price",
                    "value": f"${price:.2f}",
                    "inline": True
                },
                {
                    "name": f"{tf_emoji} Timeframe",
                    "value": timeframe.upper(),
                    "inline": True
                },
                {
                    "name": "📊 Confidence",
                    "value": f"{confidence * 100:.1f}%",
                    "inline": True
                },
                {
                    "name": "⏰ Time",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Trading Bot - {ticker} {timeframe}"
            }
        }
        
        # Add detailed indicator fields if provided
        if indicators:
            detailed_indicators = self._format_detailed_indicators(indicators, signal_type)
            if detailed_indicators:
                embed["fields"].append({
                    "name": "📈 Indicator Details",
                    "value": detailed_indicators,
                    "inline": False
                })
        
        return embed
    
    async def send_signal(self, signal_type: SignalType, 
                         ticker: str, ticker_display: str, price: float, 
                         timeframe: str, confidence: float,
                         indicators: Optional[Dict[str, Any]] = None,
                         description: Optional[str] = None) -> bool:
        """
        Send a trading signal to the appropriate Discord channel for the timeframe.
        
        Args:
            signal_type: Type of signal (BUY, SELL, ALERT, ERROR)
            ticker: Stock ticker symbol
            ticker_display: Display name for ticker
            price: Current price
            timeframe: Timeframe (e.g., '5m')
            confidence: Signal confidence (0-1)
            indicators: Dictionary of indicator values
            description: Additional description
            
        Returns:
            True if successful, False otherwise
        """
        # Get channel ID for this timeframe
        channel_id = self.channels.get(timeframe)
        if not channel_id:
            print(f"❌ No channel configured for timeframe: {timeframe}")
            return False
        
        embed = self._create_embed(signal_type, ticker, ticker_display, price, timeframe, confidence, indicators, description)
        return await self.send_to_channel(channel_id, embed)
    
    async def send_buy_signal(self, ticker: str, ticker_display: str, price: float, 
                             timeframe: str, confidence: float,
                             indicators: Optional[Dict[str, Any]] = None) -> bool:
        """Send a BUY signal to Discord."""
        return await self.send_signal(
            SignalType.BUY, ticker, ticker_display, price, timeframe, confidence, indicators,
            f"📈 Buy opportunity detected on {timeframe} chart for {ticker_display}"
        )
    
    async def send_sell_signal(self, ticker: str, ticker_display: str, price: float, 
                              timeframe: str, confidence: float,
                              indicators: Optional[Dict[str, Any]] = None) -> bool:
        """Send a SELL signal to Discord."""
        return await self.send_signal(
            SignalType.SELL, ticker, ticker_display, price, timeframe, confidence, indicators,
            f"📉 Sell opportunity detected on {timeframe} chart for {ticker_display}"
        )
    
    async def send_alert(self, message: str, timeframe: str = '1h', ticker: Optional[str] = None) -> bool:
        """Send a general alert to Discord."""
        channel_id = self.channels.get(timeframe, list(self.channels.values())[0])
        embed = {
            "title": "⚠️ ALERT",
            "description": message,
            "color": self.COLORS['ALERT'],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "footer": {"text": "Trading Bot Alert System"}
        }
        return await self.send_to_channel(channel_id, embed)
    
    async def send_error(self, error_message: str, timeframe: str = '1h', ticker: Optional[str] = None) -> bool:
        """Send an error alert to Discord."""
        channel_id = self.channels.get(timeframe, list(self.channels.values())[0])
        embed = {
            "title": "🚨 ERROR",
            "description": f"⚠️ {error_message}",
            "color": self.COLORS['ERROR'],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "footer": {"text": "Trading Bot Error"}
        }
        return await self.send_to_channel(channel_id, embed)
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
    
    def send_signal_sync(self, signal_type: SignalType, 
                        ticker: str, ticker_display: str, price: float, 
                        timeframe: str, confidence: float,
                        indicators: Optional[Dict[str, Any]] = None,
                        description: Optional[str] = None) -> bool:
        """
        Synchronous wrapper for send_signal.
        Use this in synchronous code.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                task = asyncio.create_task(
                    self.send_signal(signal_type, ticker, ticker_display, price, timeframe, confidence, indicators, description)
                )
                return task
            else:
                return loop.run_until_complete(
                    self.send_signal(signal_type, ticker, ticker_display, price, timeframe, confidence, indicators, description)
                )
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.send_signal(signal_type, ticker, ticker_display, price, timeframe, confidence, indicators, description)
            )
            loop.close()
            return result
    
    def send_buy_signal_sync(self, ticker: str, ticker_display: str, price: float, 
                            timeframe: str, confidence: float,
                            indicators: Optional[Dict[str, Any]] = None) -> bool:
        """Synchronous wrapper for send_buy_signal."""
        return self.send_signal_sync(
            SignalType.BUY, ticker, ticker_display, price, timeframe, confidence, indicators
        )
    
    def send_sell_signal_sync(self, ticker: str, ticker_display: str, price: float, 
                             timeframe: str, confidence: float,
                             indicators: Optional[Dict[str, Any]] = None) -> bool:
        """Synchronous wrapper for send_sell_signal."""
        return self.send_signal_sync(
            SignalType.SELL, ticker, ticker_display, price, timeframe, confidence, indicators
        )
