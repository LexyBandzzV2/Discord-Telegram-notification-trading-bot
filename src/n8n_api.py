"""
n8n Integration API for Trading Bot
====================================
This module provides REST API endpoints for n8n workflow integration.
Allows n8n to trigger trading analysis and receive structured results.

Usage with n8n:
1. Install Flask: pip install flask
2. Run this server: python n8n_api.py
3. Configure n8n HTTP Request node to call endpoints

Endpoints:
- POST /analyze: Run full trading analysis
- GET /status: Check bot status
- POST /export: Export signals to file
"""

import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Dict, Any

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our trading bot modules
from data_fetcher import get_available_providers
from indicators import generate_signals
# TradingBot class moved inline below

app = Flask(__name__)

# Global bot instance (reused for efficiency)
current_bot = None

@app.route('/status', methods=['GET'])
def get_status():
    """Check API and bot status."""
    providers = get_available_providers()

    status = {
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'providers': providers,
        'bot_active': current_bot is not None
    }

    if current_bot:
        status['current_ticker'] = current_bot.ticker
        status['data_points'] = len(current_bot.raw_data) if current_bot.raw_data is not None else 0
        status['signals_found'] = len(current_bot.signal_data[current_bot.signal_data['ENTRY_SIGNAL'] != 0]) if current_bot.signal_data is not None else 0

    return jsonify(status)

@app.route('/analyze', methods=['POST'])
def analyze_ticker():
    """
    Run trading analysis for a ticker.

    Expected JSON payload:
    {
        "ticker": "TSLA",
        "start_date": "2024-01-01",
        "end_date": null,
        "enable_breakout_filter": true,
        "data_provider": "yahoo",
        "provider_config": {}
    }
    """
    try:
        # Parse request data
        data = request.get_json()

        if not data or 'ticker' not in data:
            return jsonify({
                'error': 'Missing ticker parameter',
                'example': {
                    'ticker': 'TSLA',
                    'start_date': '2024-01-01',
                    'end_date': None,
                    'enable_breakout_filter': True,
                    'data_provider': 'yahoo'
                }
            }), 400

        # Extract parameters with defaults
        ticker = data['ticker']
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date')
        enable_breakout_filter = data.get('enable_breakout_filter', True)
        data_provider = data.get('data_provider', 'yahoo')
        provider_config = data.get('provider_config', {})

        print(f"🔄 Starting analysis for {ticker}...")

        # Create and run bot
        global current_bot
        current_bot = TradingBot(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            enable_breakout_filter=enable_breakout_filter,
            data_provider=data_provider,
            verbose=False,
            **provider_config
        )

        success = current_bot.run_full_analysis()

        if not success:
            return jsonify({
                'error': 'Analysis failed',
                'ticker': ticker
            }), 500

        # Get signals
        signals = current_bot.get_signals(last_n=20)

        # Prepare response
        response = {
            'success': True,
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'data_points': len(current_bot.raw_data),
            'signals_found': len(signals) if signals is not None else 0,
            'breakout_filter': enable_breakout_filter,
            'data_provider': data_provider
        }

        # Add signal details if found
        if signals is not None and not signals.empty:
            signal_list = []
            for idx, row in signals.iterrows():
                signal = {
                    'date': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'signal_type': 'BUY' if row['ENTRY_SIGNAL'] == 1 else 'SELL',
                    'price': float(row['Close']),
                    'volume': int(row['Volume']) if 'Volume' in row else None
                }

                # Add optional fields if available
                if 'SIGNAL_QUALITY' in row:
                    signal['quality'] = float(row['SIGNAL_QUALITY'])
                if 'BREAKOUT_RANK' in row and row['BREAKOUT_RANK'] > 0:
                    signal['breakout_rank'] = int(row['BREAKOUT_RANK'])

                signal_list.append(signal)

            response['signals'] = signal_list

            # Summary stats
            buy_signals = [s for s in signal_list if s['signal_type'] == 'BUY']
            sell_signals = [s for s in signal_list if s['signal_type'] == 'SELL']

            response['summary'] = {
                'total_signals': len(signal_list),
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'latest_signal': signal_list[-1] if signal_list else None
            }
        else:
            response['signals'] = []
            response['summary'] = {'total_signals': 0, 'buy_signals': 0, 'sell_signals': 0}

        print(f"✅ Analysis complete for {ticker}: {response['signals_found']} signals found")

        return jsonify(response)

    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'error': str(e),
            'ticker': data.get('ticker') if 'data' in locals() else 'unknown'
        }), 500

@app.route('/export', methods=['POST'])
def export_signals():
    """
    Export signals to CSV file.

    Expected JSON payload:
    {
        "filename": "signals_20241201.csv"
    }
    """
    try:
        if current_bot is None or current_bot.signal_data is None:
            return jsonify({'error': 'No analysis data available. Run /analyze first.'}), 400

        data = request.get_json() or {}
        filename = data.get('filename', f"signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")

        # Export signals
        success = current_bot.export_signals(filename)

        if success:
            return jsonify({
                'success': True,
                'filename': filename,
                'signals_exported': len(current_bot.signal_data[current_bot.signal_data['ENTRY_SIGNAL'] != 0])
            })
        else:
            return jsonify({'error': 'Export failed'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers', methods=['GET'])
def list_providers():
    """List available data providers and their status."""
    providers = get_available_providers()

    provider_info = {
        'yahoo': {
            'available': providers['yahoo'],
            'description': 'Yahoo Finance (free, delayed futures)',
            'instruments': ['Stocks', 'ETFs', 'Delayed Futures']
        },
        'ibkr': {
            'available': providers['ibkr'],
            'description': 'Interactive Brokers (real-time futures)',
            'instruments': ['Stocks', 'Futures', 'Options'],
            'setup_required': not providers['ibkr']
        },
        'alpaca': {
            'available': providers['alpaca'],
            'description': 'Alpaca (stocks & crypto futures)',
            'instruments': ['Stocks', 'Crypto Futures'],
            'setup_required': not providers['alpaca']
        }
    }

    return jsonify({
        'providers': provider_info,
        'installation_commands': {
            'ibkr': 'pip install ib_insync',
            'alpaca': 'pip install alpaca-py'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting n8n Integration API...")
    print("📡 Server will run on http://localhost:5000")
    print("\n📋 Available endpoints:")
    print("  GET  /status     - Check API status")
    print("  POST /analyze    - Run trading analysis")
    print("  POST /export     - Export signals to CSV")
    print("  GET  /providers  - List data providers")
    print("\n🔧 n8n Configuration:")
    print("  Use HTTP Request node with POST to http://localhost:5000/analyze")
    print("  Content-Type: application/json")
    print("\n⚠️  Press Ctrl+C to stop the server")

    app.run(host='0.0.0.0', port=5000, debug=False)