import asyncio
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from config.config import Config

def test_analyze_ticker():
    config = Config()
    analyzer = MultiTimeframeAnalyzer(config)

    ticker = 'AAPL'
    timeframe = '1d'

    async def run_test():
        print(f"Analyzing {ticker} on {timeframe}...")
        result = await analyzer.analyze_ticker_timeframe(ticker, timeframe)

        if result:
            print("✅ Analysis successful:")
            print(result)
        else:
            print("❌ Analysis failed or no signals generated.")

    asyncio.run(run_test())

if __name__ == "__main__":
    test_analyze_ticker()