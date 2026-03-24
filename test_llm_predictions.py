import asyncio
from src.llm_wrapper import LLMWrapper
from config.config import Config

def test_generate_daily_summary():
    config = Config()
    llm = LLMWrapper(api_key=config.GOOGLE_API_KEY, model=config.LLM_MODEL)

    scan_results = {
        "1d": [
            {
                "ticker": "AAPL",
                "signal": "BUY",
                "price": 150.0,
                "confidence": 0.9,
                "indicators": {
                    "stoch_status": "Overbought",
                    "alligator_status": "Trending Up",
                    "vortex_status": "Bullish"
                }
            }
        ]
    }

    strategy_params = {
        "name": "Momentum Strategy",
        "indicators": {
            "Alligator": {"jaw": 13, "teeth": 8, "lips": 5},
            "Stochastic": {"k": 14, "d": 3},
            "Vortex": {"vi+": 14, "vi-": 14}
        },
        "entry_rules": ["Buy when Stochastic crosses above 20"],
        "risk_management": {"stop_loss": "2%", "take_profit": "5%"}
    }

    async def run_test():
        print("Generating daily summary...")
        summary = await llm.generate_daily_summary(scan_results, strategy_params)
        print("Summary:")
        print(summary)

    asyncio.run(run_test())

if __name__ == "__main__":
    test_generate_daily_summary()