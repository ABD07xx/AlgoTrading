# Automated Crypto Trading Bot

An automated cryptocurrency trading bot built in Python that implements technical analysis strategies for algorithmic trading. The bot currently supports BTC-INR trading with configurable risk management and technical indicators.

## Features

- Real-time market data fetching from Yahoo Finance
- Configurable technical indicators:
  - RSI (Relative Strength Index)
  - EMA (Exponential Moving Average)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - ATR (Average True Range)
- Risk management:
  - Configurable position sizing
  - Stop-loss orders
  - Trailing stops
  - Take-profit targets
  - Leverage support (up to 100x)
- Multiple trading strategies:
  - Aggressive (scalping) configuration
  - Conservative configuration
- Paper trading account with detailed trade history
- Automated trade execution
- Performance tracking and analytics

## Installation

1. Clone the repository:
bash
git clone https://github.com/yourusername/crypto-trading-bot.git
cd crypto-trading-bot


2. Install required dependencies:

bash
pip install -r requirements.txt


## Configuration

The bot supports two main configuration profiles:

### Aggressive Configuration (aggressive_config.py)
- Short timeframe (1-minute candles)
- Higher risk tolerance
- Frequent trading opportunities
- Lower profit targets

### Conservative Configuration (conservative_config.py)
- Longer timeframe (1-hour candles)
- Lower risk tolerance
- Stricter entry conditions
- Higher profit targets

## Usage

1. Start the bot with aggressive configuration:

bash
python run_trader.py


2. To use conservative configuration, modify run_trader.py to uncomment the conservative trader initialization.

## Trade Results

The bot maintains several JSON files for tracking:

- `paper_account.json`: Current account state and positions
- `trade_results.json`: Detailed trade history and performance metrics
- `trade_log.json`: Comprehensive trading logs

## GitHub Actions Integration

The bot is configured to run automatically every 5 minutes using GitHub Actions. The workflow:
- Fetches latest market data
- Executes trading strategy
- Updates trading results
- Commits changes back to the repository
