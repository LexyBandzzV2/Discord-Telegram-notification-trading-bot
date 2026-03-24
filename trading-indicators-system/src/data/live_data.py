class LiveData:
    def __init__(self, api_connector):
        self.api_connector = api_connector

    def fetch_live_data(self, symbol, interval='1m'):
        return self.api_connector.get_ohlc_data(symbol, interval)

    def get_latest_price(self, symbol):
        data = self.fetch_live_data(symbol)
        return data[-1]['close'] if data else None

    def get_historical_data(self, symbol, limit=100):
        return self.api_connector.get_historical_data(symbol, limit)