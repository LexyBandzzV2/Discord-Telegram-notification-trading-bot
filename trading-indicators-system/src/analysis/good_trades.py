class GoodTrades:
    def __init__(self):
        self.good_trades = []

    def log_trade(self, trade_data):
        self.good_trades.append(trade_data)

    def get_good_trades(self):
        return self.good_trades

    def analyze_performance(self):
        if not self.good_trades:
            return {"total_trades": 0, "profit": 0}

        total_trades = len(self.good_trades)
        total_profit = sum(trade['profit'] for trade in self.good_trades)
        return {"total_trades": total_trades, "profit": total_profit}