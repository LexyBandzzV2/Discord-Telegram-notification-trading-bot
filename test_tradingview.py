#!/usr/bin/env python
"""Test TradingView data fetching."""

from src.data_fetcher import DataFetcher

print("=" * 60)
print("TESTING TRADINGVIEW DATA FETCHING")
print("=" * 60)

# Test TradingView fetcher
fetcher = DataFetcher(provider='tradingview')

# Test 1: ES (S&P 500 Futures)
print("\n1. Fetching ES (S&P 500 Futures) - Daily bars")
print("-" * 60)
try:
    data = fetcher.fetch('ES', '2024-12-01', '2024-12-13', interval='1d')
    print(f"✓ Successfully fetched {len(data)} bars")
    close_price = data["Close"].iloc[-1]
    high_price = data["High"].iloc[-1]
    low_price = data["Low"].iloc[-1]
    volume = int(data["Volume"].iloc[-1])
    print(f"Latest close: {close_price:.2f}")
    print(f"Latest high:  {high_price:.2f}")
    print(f"Latest low:   {low_price:.2f}")
    print(f"Latest volume: {volume:,}")
    print(f"Date range: {data.index[0].date()} to {data.index[-1].date()}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: NQ (NASDAQ Futures)
print("\n2. Fetching NQ (NASDAQ Futures) - Daily bars")
print("-" * 60)
try:
    data = fetcher.fetch('NQ', '2024-12-01', '2024-12-13', interval='1d')
    print(f"✓ Successfully fetched {len(data)} bars")
    close_price = data["Close"].iloc[-1]
    print(f"Latest close: {close_price:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: BTC (Bitcoin)
print("\n3. Fetching BTCUSD (Bitcoin) - Daily bars")
print("-" * 60)
try:
    data = fetcher.fetch('BTCUSD', '2024-12-01', '2024-12-13', interval='1d')
    print(f"✓ Successfully fetched {len(data)} bars")
    close_price = data["Close"].iloc[-1]
    print(f"Latest close: ${close_price:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("TRADINGVIEW SETUP COMPLETE! ✓")
print("=" * 60)
