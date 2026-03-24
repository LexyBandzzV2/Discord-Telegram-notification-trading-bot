class BadTrades:
    def __init__(self):
        self.bad_trades = []

    def log_trade(self, trade_details):
        self.bad_trades.append(trade_details)

    def get_bad_trades(self):
        return self.bad_trades

    def analyze_trades(self):
        # Placeholder for analysis logic
        pass