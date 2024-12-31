# Aggressive/Scalping Configuration
# Aims for frequent trades with smaller profits

CONFIG = {
    'symbol': 'BTC-INR',
    'timeframe': '1m',        # 1-minute candles
    'risk_percent': 2.0,      # Increased from 0.5% to 2%
    'initial_balance': 10000,
    'leverage': 100,    # Added leverage parameter
    
    # Technical Parameters
    'rsi_period': 7,         # Shorter RSI for faster signals
    'rsi_overbought': 70,    # More aggressive RSI levels
    'rsi_oversold': 30,      # More lenient RSI levels
    'atr_period': 14,
    
    'ema_fast': 8,
    'ema_slow': 13,
    'ema_trend': 21,
    
    'volume_threshold': 0.1,  # Much lower volume requirement
    
    # Risk Management
    'profit_target': 0.3,     # Increased from 0.15% to 0.3%
    'stop_loss': 0.2,        # Increased from 0.1% to 0.2%
    'trailing_stop': True,
    'trailing_stop_atr': 1.5,
    
    # Trade Conditions
    'min_conditions': 1,     # Only need 1 condition (super aggressive)
    
    # Filters
    'use_volume_filter': False,
    'use_trend_filter': False,
    'use_volatility_filter': False
} 