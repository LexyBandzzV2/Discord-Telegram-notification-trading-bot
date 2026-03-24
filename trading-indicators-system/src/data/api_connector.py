class APIConnector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.example.com"  # Replace with actual API base URL

    def get_data(self, endpoint, params=None):
        import requests
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def fetch_market_data(self, symbol):
        endpoint = "market_data"
        params = {"symbol": symbol}
        return self.get_data(endpoint, params)

    def fetch_historical_data(self, symbol, start_date, end_date):
        endpoint = "historical_data"
        params = {"symbol": symbol, "start": start_date, "end": end_date}
        return self.get_data(endpoint, params)