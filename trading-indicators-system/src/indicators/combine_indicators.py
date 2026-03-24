class CombineIndicators:
    def __init__(self):
        self.indicators = []

    def add_indicator(self, indicator):
        self.indicators.append(indicator)

    def calculate_signals(self, data):
        signals = {}
        for indicator in self.indicators:
            signals[indicator.name] = indicator.calculate(data)
        return signals

    def combine_signals(self, signals):
        buy_signals = all(signal == 'buy' for signal in signals.values())
        sell_signals = all(signal == 'sell' for signal in signals.values())
        
        if buy_signals:
            return "buy"
        elif sell_signals:
            return "sell"
        else:
            return "hold"