import pandas as pd
import ta
import yfinance as yf
from typing import Optional
from indicators import generate_signals

def to_heikin_ashi(df: pd.DataFrame, keep_original: bool = False) -> pd.DataFrame:
    """
    Converts standard OHLCV DataFrame to Heikin-Ashi OHLCV.
    
    Args:
        df: DataFrame with OHLCV columns (Open, High, Low, Close, Volume)
        keep_original: If True, keeps original OHLC as separate columns
        
    Returns:
        DataFrame with Heikin-Ashi OHLCV data
        
    Raises:
        ValueError: If required columns are missing or DataFrame is too small
    """
    # Flatten multi-index columns if present (from yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Validate input
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    if len(df) < 2:
        raise ValueError("DataFrame must have at least 2 rows for HA conversion")
    
    # Work with a copy to avoid modifying original
    ha_df = df.copy()
    
    # Store original OHLC if requested
    if keep_original:
        ha_df['Orig_Open'] = df['Open']
        ha_df['Orig_High'] = df['High']
        ha_df['Orig_Low'] = df['Low']
        ha_df['Orig_Close'] = df['Close']
    
    # Calculate Heikin-Ashi Close (average of OHLC)
    ha_df['HAC'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    # Calculate Heikin-Ashi Open (midpoint of previous HA bar)
    ha_df['HAO'] = ((df['Open'].shift(1) + df['Close'].shift(1)) / 2)
    ha_df.loc[ha_df.index[0], 'HAO'] = df['Open'].iloc[0]  # Fix: Use .loc instead of .iloc
    
    # Calculate Heikin-Ashi High and Low
    ha_df['HAH'] = ha_df[['High', 'HAO', 'HAC']].max(axis=1)
    ha_df['HAL'] = ha_df[['Low', 'HAO', 'HAC']].min(axis=1)
    
    # Replace original OHLC with HA values
    ha_df['Open'] = ha_df['HAO']
    ha_df['High'] = ha_df['HAH']
    ha_df['Low'] = ha_df['HAL']
    ha_df['Close'] = ha_df['HAC']
    
    # Drop intermediate calculation columns
    ha_df = ha_df.drop(['HAO', 'HAH', 'HAL', 'HAC'], axis=1)
    
    # Drop first row with NaN (from shift operation)
    ha_df = ha_df.dropna()
    
    return ha_df


# --- Example Usage ---
if __name__ == "__main__":
    ticker = "AAPL"
    print(f"Fetching data for {ticker}...") # Change the ticker symbol (line 68) to any stock you want to analyze
    
    # Fetch data
    df = yf.download(ticker, start="2024-01-01", progress=False) # You can change the start date (line 71) to any date you want to analyze from
    # "2023-01-01" - Get 2 years of data
    
    if df.empty:
        print("No data fetched. Check ticker symbol and date range.")
    else:
        print(f"Fetched {len(df)} rows of data")
        
        # Convert to Heikin-Ashi
        ha_df = to_heikin_ashi(df, keep_original=True)
        
        # Generate trading signals
        ha_df = generate_signals(ha_df, enable_breakout_filter=True)
        
        print(f"\nOriginal OHLC (last 5 rows):")
        print(df[['Open', 'High', 'Low', 'Close']].tail())
        
        print(f"\nHeikin-Ashi OHLC (last 5 rows):")
        print(ha_df[['Open', 'High', 'Low', 'Close']].tail())
        
        # Print signals
        print("\nTrading Signals:")
        print(ha_df[ha_df['ENTRY_SIGNAL'] != 0][['Open', 'High', 'Low', 'Close', 'ENTRY_SIGNAL', 'SIGNAL_QUALITY']].tail(10))

# what it can do:
# - Fetch historical stock data using yfinance
# - Fetches AAPL stock data from Yahoo Finance (starting from 2024-01-01)
# - Converts it to Heikin-Ashi format
# - Displays the results showing both original and HA OHLC data

# Next steps:
# - Integrate with trading strategies
# - Add technical indicators based on the Heikin-Ashi data