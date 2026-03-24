"""
Test script for multi-timeframe analysis with Discord notifications.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from config.config import Config
from src.multi_timeframe_analyzer import MultiTimeframeAnalyzer


async def test_multi_timeframe():
    """Test multi-timeframe analysis."""
    print("\n" + "="*80)
    print("🚀 MULTI-TIMEFRAME TRADING BOT TEST")
    print("="*80)
    
    # Validate config
    is_valid, message = Config.validate()
    print(f"\n{message}")
    
    if not is_valid:
        print("\n❌ Configuration invalid - aborting test")
        return
    
    # Print config
    Config.print_config()
    
    # Run analyzer
    analyzer = MultiTimeframeAnalyzer()
    
    try:
        results = await analyzer.analyze_all()
        print("\n✅ Multi-timeframe analysis complete!")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await analyzer.close()


if __name__ == "__main__":
    asyncio.run(test_multi_timeframe())
