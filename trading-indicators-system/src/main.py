from data.api_connector import APIConnector
from data.live_data import LiveData
from indicators.combine_indicators import CombineIndicators
from analysis.good_trades import GoodTrades
from analysis.bad_trades import BadTrades

def main():
    # Initialize API Connector
    api_connector = APIConnector(api_key='YOUR_API_KEY')
    
    # Fetch live data
    live_data = LiveData(api_connector)
    
    # Initialize indicators
    indicators = CombineIndicators()
    
    # Initialize trade analysis
    good_trades = GoodTrades()
    bad_trades = BadTrades()
    
    # Main loop to process live data
    while True:
        # Fetch OHLC data
        ohlc_data = live_data.get_ohlc_data()
        
        # Calculate indicators
        signals = indicators.calculate_signals(ohlc_data)
        
        # Determine trade actions
        if signals['buy']:
            good_trades.log_trade(ohlc_data)
            print("Buy Signal")
        elif signals['sell']:
            bad_trades.log_trade(ohlc_data)
            print("Sell Signal")

if __name__ == "__main__":
    main()