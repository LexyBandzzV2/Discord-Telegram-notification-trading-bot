from src.data_fetcher import DataFetcher
from datetime import datetime, timedelta

# Initialize DataFetcher with Yahoo as the provider
fetcher = DataFetcher(provider='yahoo')

# Test parameters
ticker = 'TSLA'
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')
interval = '1d'

# Fetch data and print results
try:
    data = fetcher.fetch(ticker=ticker, start=start_date, end=end_date, interval=interval)
    print(f"Data fetched for {ticker} ({interval}):\n", data.tail())
except Exception as e:
    print(f"Error fetching data for {ticker}: {e}")