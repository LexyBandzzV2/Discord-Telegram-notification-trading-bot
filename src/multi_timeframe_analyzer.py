"""
Multi-Timeframe Analyzer
========================
Analyzes multiple tickers across different timeframes (1m, 3m, 5m, 15m, 1h)
and generates trading signals for each combination.

Usage:
    analyzer = MultiTimeframeAnalyzer()
    await analyzer.analyze_all()
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.data_fetcher import DataFetcher
from src.discord_notifier import DiscordNotifier
from src.indicators import generate_signals
from config.config import Config


class MultiTimeframeAnalyzer:
    """Analyzes multiple tickers across different timeframes."""
    
    def __init__(self, config: Config = None):
        """
        Initialize the analyzer.
        
        Args:
            config: Configuration object (defaults to Config)
        """
        self.config = config or Config()
        self.data_fetcher = DataFetcher(provider=self.config.DATA_PROVIDER)
        self.notifier = DiscordNotifier(
            bot_token=self.config.DISCORD_BOT_TOKEN,
            channels=self.config.DISCORD_CHANNELS
        )
        
        # Store previous signals to avoid duplicate notifications
        self.previous_signals = {}
    
    def _format_indicator_details(self, data: pd.DataFrame, signal: str) -> Dict[str, any]:
        """
        Format detailed indicator information from dataframe.
        
        Args:
            data: DataFrame with indicator columns
            signal: 'BUY' or 'SELL'
            
        Returns:
            Dictionary with formatted indicator details
        """
        last_row = data.iloc[-1]
        indicators = {}
        
        # Price
        indicators['price'] = last_row['Close']
        
        # Stochastic RSI Details
        if 'STOCHk_14_3_3' in data.columns and 'STOCHd_14_3_3' in data.columns:
            stoch_k = last_row['STOCHk_14_3_3']
            stoch_d = last_row['STOCHd_14_3_3']
            
            # Check if touching overbought (80) or oversold (20) lines
            if stoch_k >= 80 or stoch_d >= 80:
                indicators['stoch_status'] = "Overbought (touching 80+ line)"
            elif stoch_k <= 20 or stoch_d <= 20:
                indicators['stoch_status'] = "Oversold (touching 20- line)"
            else:
                indicators['stoch_status'] = f"Mid-Range (K:{stoch_k:.1f}, D:{stoch_d:.1f})"
            
            indicators['stoch_k'] = stoch_k
            indicators['stoch_d'] = stoch_d
        
        # Alligator Details - Check if green line (LIPS) is crossing
        if 'ALLIGATOR_LIPS' in data.columns and 'ALLIGATOR_TEETH' in data.columns and 'ALLIGATOR_JAW' in data.columns:
            lips = last_row['ALLIGATOR_LIPS']
            teeth = last_row['ALLIGATOR_TEETH']
            jaw = last_row['ALLIGATOR_JAW']
            lips_prev = data['ALLIGATOR_LIPS'].iloc[-2] if len(data) > 1 else lips
            
            # Determine crossing direction
            if signal == 'BUY':
                if lips > lips_prev and (lips > teeth or lips > jaw):
                    crossing_lines = []
                    if lips > teeth:
                        crossing_lines.append("red line")
                    if lips > jaw:
                        crossing_lines.append("blue line")
                    if len(crossing_lines) == 2:
                        crossing_text = "crossed red and blue lines"
                    elif len(crossing_lines) == 1:
                        crossing_text = f"crossed {crossing_lines[0]}"
                    else:
                        crossing_text = "no cross"
                    indicators['alligator_status'] = f"Green Cross-Up ({crossing_text})"
                else:
                    indicators['alligator_status'] = "Green Cross-Up (no cross)"
            else:  # SELL
                if lips < lips_prev and (lips < teeth or lips < jaw):
                    crossing_lines = []
                    if lips < teeth:
                        crossing_lines.append("red line")
                    if lips < jaw:
                        crossing_lines.append("blue line")
                    if len(crossing_lines) == 2:
                        crossing_text = "crossed red and blue lines"
                    elif len(crossing_lines) == 1:
                        crossing_text = f"crossed {crossing_lines[0]}"
                    else:
                        crossing_text = "no cross"
                    indicators['alligator_status'] = f"Green Cross-Down ({crossing_text})"
                else:
                    indicators['alligator_status'] = "Green Cross-Down (no cross)"
        
        # Vortex Details - Check crossing status
        if 'VIp_14' in data.columns and 'VIm_14' in data.columns:
            vi_pos = last_row['VIp_14']  # Green line
            vi_neg = last_row['VIm_14']  # Red line
            vi_pos_prev = data['VIp_14'].iloc[-2] if len(data) > 1 else vi_pos
            vi_neg_prev = data['VIm_14'].iloc[-2] if len(data) > 1 else vi_neg
            
            # Determine crossing direction
            if signal == 'BUY':
                # Green line (VI+) should be crossing above red line (VI-)
                if vi_pos > vi_neg and vi_pos_prev <= vi_neg_prev:
                    indicators['vortex_status'] = "Green cross - VI+ crossing above VI- (uptrend)"
                elif vi_pos > vi_neg:
                    indicators['vortex_status'] = "Green cross - VI+ above VI- (uptrend)"
                else:
                    indicators['vortex_status'] = "Vortex mixed signals"
            else:  # SELL
                # Red line (VI-) should be crossing above green line (VI+)
                if vi_neg > vi_pos and vi_neg_prev <= vi_pos_prev:
                    indicators['vortex_status'] = "Red cross - VI- crossing above VI+ (downtrend)"
                elif vi_neg > vi_pos:
                    indicators['vortex_status'] = "Red cross - VI- above VI+ (downtrend)"
                else:
                    indicators['vortex_status'] = "Vortex mixed signals"
        
        return indicators
    
    async def analyze_ticker_timeframe(self, ticker: str, timeframe: str) -> Optional[Dict]:
        """
        Analyze a single ticker on a specific timeframe.
        
        Args:
            ticker: Stock ticker (e.g., 'TSLA')
            timeframe: Timeframe (e.g., '5m')
            
        Returns:
            Dictionary with signal info or None
        """
        try:
            # Calculate lookback period
            lookback_days = self.config.TIMEFRAME_LOOKBACK.get(timeframe, 5)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            
            print(f"  📊 Analyzing {ticker} on {timeframe}...", end=" ")
            
            # Fetch data
            data = self.data_fetcher.fetch(
                ticker=ticker,
                start=start_date,
                end=end_date,
                interval=timeframe
            )
            
            if data.empty:
                print("❌ No data")
                return None
            
            if len(data) < 5:
                print(f"⚠️  Insufficient data ({len(data)} bars)")
                return None
            
            # Drop NaN rows and reset index
            data = data.dropna()
            if len(data) < 5:
                print(f"⚠️  Insufficient valid data ({len(data)} bars after cleaning)")
                return None
            
            if len(data) < 50:
                print(f"⚠️  Not enough data for 50-period average. Available bars: {len(data)}")
                return None

            # Calculate indicators
            try:
                data = generate_signals(data, enable_breakout_filter=False)
            except Exception as gen_err:
                print(f"❌ Error generating signals: {gen_err}")
                return None

            # Simulate signal analysis (using last 3 candles)
            try:
                last_candle = data.iloc[-1]
                close_price = last_candle['Close']
            except IndexError as idx_err:
                print(f"❌ Index error accessing last candle: {idx_err}")
                return None
            
            # Simple signal: if close > 52-week average = buy, else sell
            avg_50 = data['Close'].tail(50).mean() if len(data) >= 50 else data['Close'].mean()
            
            signal = None
            confidence = 0.0
            
            if close_price > avg_50 * 1.02:  # 2% above average
                signal = 'BUY'
                confidence = min(0.95, 0.6 + ((close_price - avg_50) / avg_50) * 5)
            elif close_price < avg_50 * 0.98:  # 2% below average
                signal = 'SELL'
                confidence = min(0.95, 0.6 + ((avg_50 - close_price) / avg_50) * 5)
            
            if signal:
                print(f"✓ {signal}")
                
                # Get detailed indicator information
                indicator_details = self._format_indicator_details(data, signal)
                
                return {
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'signal': signal,
                    'price': close_price,
                    'confidence': confidence,
                    'indicators': indicator_details,
                    'timestamp': datetime.now()
                }
            
            print("⊙ Hold")
            return None
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def process_signal(self, signal_data: Dict) -> bool:
        """
        Process a signal and send to Discord if new.
        
        Args:
            signal_data: Signal dictionary from analyze_ticker_timeframe
            
        Returns:
            True if signal was sent, False otherwise
        """
        ticker = signal_data['ticker']
        timeframe = signal_data['timeframe']
        signal_type = signal_data['signal']
        
        # Create signal key to check for duplicates
        signal_key = f"{ticker}_{timeframe}_{signal_type}"
        
        # Skip if we just sent this signal
        if signal_key in self.previous_signals:
            last_sent = self.previous_signals[signal_key]
            if (datetime.now() - last_sent).seconds < 300:  # 5 minute minimum
                return False
        
        # Get display names
        ticker_display = self.config.get_ticker_display_name(ticker)
        
        # Send appropriate signal
        try:
            if signal_type == 'BUY':
                await self.notifier.send_buy_signal(
                    ticker=ticker,
                    ticker_display=ticker_display,
                    price=signal_data['price'],
                    timeframe=timeframe,
                    confidence=signal_data['confidence'],
                    indicators=signal_data.get('indicators')
                )
            else:  # SELL
                await self.notifier.send_sell_signal(
                    ticker=ticker,
                    ticker_display=ticker_display,
                    price=signal_data['price'],
                    timeframe=timeframe,
                    confidence=signal_data['confidence'],
                    indicators=signal_data.get('indicators')
                )
            
            # Record this signal
            self.previous_signals[signal_key] = datetime.now()
            print(f"   ✓ Discord notification sent!")
            return True
            
        except Exception as e:
            print(f"   ❌ Error sending signal: {e}")
            return False
    
    async def analyze_all(self) -> Dict[str, List[Dict]]:
        """
        Analyze all configured tickers across all timeframes.
        
        Returns:
            Dictionary with signals for each timeframe
        """
        print("\n" + "=" * 80)
        print("🚀 MULTI-TIMEFRAME ANALYSIS - STARTED")
        print("=" * 80)
        print(f"📊 Tickers: {', '.join(self.config.PRIMARY_TICKERS)}")
        print(f"⏱️  Timeframes: {', '.join(self.config.TIMEFRAMES)}")
        print("=" * 80 + "\n")
        
        results = {tf: [] for tf in self.config.TIMEFRAMES}
        
        # Create all analysis tasks
        tasks = []
        for ticker in self.config.PRIMARY_TICKERS:
            for timeframe in self.config.TIMEFRAMES:
                tasks.append(self.analyze_ticker_timeframe(ticker, timeframe))
        
        # Run all analyses in parallel
        signal_list = await asyncio.gather(*tasks)
        
        # Process signals
        for signal_data in signal_list:
            if signal_data:
                await self.process_signal(signal_data)
                results[signal_data['timeframe']].append(signal_data)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: Dict[str, List[Dict]]):
        """Print analysis summary."""
        print("\n" + "=" * 80)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 80)
        
        total_signals = sum(len(v) for v in results.values())
        
        for timeframe in self.config.TIMEFRAMES:
            signals = results[timeframe]
            emoji = self.notifier.TIMEFRAME_EMOJIS.get(timeframe, '⏱️')
            
            if signals:
                print(f"\n{emoji} {timeframe.upper()}:")
                for sig in signals:
                    ticker_display = self.config.get_ticker_display_name(sig['ticker'])
                    signal_emoji = "🟢" if sig['signal'] == 'BUY' else "🔴"
                    print(f"   {signal_emoji} {ticker_display}: {sig['signal']} @ ${sig['price']:.2f} ({sig['confidence']*100:.0f}%)")
            else:
                print(f"\n{emoji} {timeframe.upper()}: No signals")
        
        print(f"\n📈 Total Signals: {total_signals}")
        print("=" * 80 + "\n")
    
    async def run_continuous(self, interval_minutes: int = 5):
        """
        Run analysis continuously at regular intervals.
        
        Args:
            interval_minutes: Interval in minutes between analyses
        """
        print(f"🔄 Starting continuous analysis (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                await self.analyze_all()
                print(f"⏳ Next analysis in {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                print(f"❌ Error in continuous analysis: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def close(self):
        """Cleanup resources."""
        await self.notifier.close()


# ==================== MAIN ENTRY POINT ====================

async def main():
    """Main function for testing."""
    analyzer = MultiTimeframeAnalyzer()
    
    try:
        # Run single analysis
        await analyzer.analyze_all()
        
        # Uncomment to run continuously
        # await analyzer.run_continuous(interval_minutes=5)
        
    finally:
        await analyzer.close()


if __name__ == "__main__":
    asyncio.run(main())
