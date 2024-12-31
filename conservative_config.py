# Conservative Configuration
# Aims for high-probability trades with larger profits

CONFIG = {
    'symbol': 'BTC-USD',
    'timeframe': '1h',        # 1-hour candles
    'risk_percent': 1,        # Standard risk per trade
    'initial_balance': 10000,
    
    # Technical Parameters
    'rsi_period': 14,        # Standard RSI
    'rsi_overbought': 70,    # Standard RSI levels
    'rsi_oversold': 30,
    'atr_period': 14,
    
    'ema_fast': 50,          # Slower EMAs for trend confirmation
    'ema_slow': 200,
    'ema_trend': 20,
    
    'volume_threshold': 1.5,  # Higher volume requirement
    
    # Risk Management
    'profit_target': 2.0,    # 2% profit target
    'stop_loss': 1.0,        # 1% stop loss
    'trailing_stop': True,
    'trailing_stop_atr': 2.5,
    
    # Trade Conditions
    'min_conditions': 4,     # Need all 4 conditions
    
    # Filters
    'use_volume_filter': True,
    'use_trend_filter': True,
    'use_volatility_filter': True
} 
