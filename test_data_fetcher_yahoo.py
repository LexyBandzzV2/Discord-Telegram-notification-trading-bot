import pandas as pd
from src.data_fetcher import DataFetcher

def test_fetch_yahoo():
    fetcher = DataFetcher(provider='yahoo')
    ticker = 'AAPL'
    start_date = '2026-01-01'
    end_date = '2026-02-01'
    interval = '1d'

    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    data = fetcher.fetch(ticker=ticker, start=start_date, end=end_date, interval=interval)

    if data.empty:
        print("❌ No data retrieved.")
    else:
        print("✅ Data retrieved successfully.")
        print(data.head())

if __name__ == "__main__":
    test_fetch_yahoo()