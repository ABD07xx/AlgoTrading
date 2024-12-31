import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
import ta

class AlgoTrader:
    def __init__(self, config):
        self.config = config
        self.symbol = config['symbol']
        self.timeframe = config['timeframe']
        self.risk_percent = config['risk_percent']
        
        # Initialize account
        self.account = self.load_account_state(config['initial_balance'])
        
    def load_account_state(self, initial_balance):
        """Load or create paper trading account"""
        if os.path.exists('paper_account.json'):
            with open('paper_account.json', 'r') as f:
                return json.load(f)
        else:
            account = {
                'balance': initial_balance,
                'positions': {},
                'trade_history': []
            }
            self.save_account_state(account)
            return account
    
    def save_account_state(self, account_state):
        """Save account state to file"""
        with open('paper_account.json', 'w') as f:
            json.dump(account_state, f, indent=4)
    
    def get_historical_data(self):
        """Fetch historical data from Yahoo Finance"""
        ticker = yf.Ticker(self.symbol)
        end = datetime.now()
        start = end - timedelta(days=5)  # 5 days of history
        df = ticker.history(start=start, end=end, interval=self.timeframe)
        
        if df.empty:
            raise ValueError("No data received from Yahoo Finance")
        return df
    
    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Trend Indicators
        df[f"ema_{self.config['ema_fast']}"] = df['Close'].ewm(span=self.config['ema_fast']).mean()
        df[f"ema_{self.config['ema_slow']}"] = df['Close'].ewm(span=self.config['ema_slow']).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        
        # Momentum
        df['rsi'] = ta.momentum.rsi(df['Close'], window=self.config['rsi_period'])
        df['macd'] = ta.trend.macd_diff(df['Close'])
        df['macd_signal'] = ta.trend.macd_signal(df['Close'])
        
        # Volatility
        df['atr'] = ta.volatility.average_true_range(
            df['High'], 
            df['Low'], 
            df['Close'],
            window=self.config['atr_period']
        )
        
        # Bollinger Bands
        indicator_bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['bb_upper'] = indicator_bb.bollinger_hband()
        df['bb_middle'] = indicator_bb.bollinger_mavg()
        df['bb_lower'] = indicator_bb.bollinger_lband()
        
        # Volume
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        return df
    
    def generate_signals(self, df):
        """Generate trading signals based on config"""
        df['signal'] = 0
        conditions_met = 0
        
        # Don't generate buy signals if we already have a position
        if self.symbol in self.account['positions']:
            # Check for sell signals only
            if (df['rsi'].iloc[-1] > self.config['rsi_overbought'] or 
                df['Close'].iloc[-1] < df[f"ema_{self.config['ema_fast']}"].iloc[-1] or
                self.check_profit_target(df) or 
                self.check_stop_loss(df)):
                df.iloc[-1, df.columns.get_loc('signal')] = -1
            return df
        
        # Continue with buy signal generation if no position...
        # 1. Trend Condition
        trend_condition = (
            (df['Close'] > df[f"ema_{self.config['ema_fast']}"]) & 
            (df[f"ema_{self.config['ema_fast']}"] > df[f"ema_{self.config['ema_slow']}"])
        )
        if trend_condition.iloc[-1]:
            conditions_met += 1
            
        # 2. Momentum Condition
        momentum_condition = (
            (df['rsi'] < self.config['rsi_oversold']) |
            (df['macd'] > df['macd_signal'])
        )
        if momentum_condition.iloc[-1]:
            conditions_met += 1
            
        # 3. Volume Condition
        volume_condition = df['volume_ratio'] > self.config['volume_threshold']
        if volume_condition.iloc[-1]:
            conditions_met += 1
            
        # 4. Volatility Condition
        volatility_condition = (
            (df['Close'] > df['bb_middle']) &
            (df['atr'] < df['atr'].rolling(window=10).mean())
        )
        if volatility_condition.iloc[-1]:
            conditions_met += 1
            
        # Generate Buy Signal - Fixed boolean indexing
        if conditions_met >= self.config['min_conditions'] and self.symbol not in self.account['positions']:
            df.iloc[-1, df.columns.get_loc('signal')] = 1
        
        # Debug prints
        self.print_market_analysis(df, conditions_met)
        
        return df
    
    def print_market_analysis(self, df, conditions_met):
        """Print market analysis with INR formatting"""
        latest = df.iloc[-1]
        print("\n=== Market Analysis ===")
        print(f"Price: ₹{latest['Close']:,.2f}")
        print(f"Conditions Met: {conditions_met}/{self.config['min_conditions']}")
        print(f"RSI: {latest['rsi']:.2f}")
        print(f"Volume Ratio: {latest['volume_ratio']:.2f}x")
        print(f"MACD Signal: {'Bullish' if latest['macd'] > latest['macd_signal'] else 'Bearish'}")
        if self.symbol in self.account['positions']:
            pos = self.account['positions'][self.symbol]
            print(f"Current P/L: {self.calculate_current_pnl(latest['Close']):.2f}%")
        print("=====================\n")
    
    def calculate_position_size(self, entry_price, stop_loss):
        """Calculate position size based on risk management"""
        risk_amount = self.account['balance'] * (self.risk_percent / 100)
        position_size = risk_amount / (entry_price - stop_loss)
        return position_size
    
    def execute_trade(self, signal, current_price, timestamp):
        """Execute paper trades with INR values"""
        try:
            if signal == 1:  # Buy signal
                if self.symbol not in self.account['positions']:
                    # Calculate position size with leverage
                    risk_amount = self.account['balance'] * (self.risk_percent / 100)
                    leveraged_position = risk_amount * self.config['leverage']
                    position_size = leveraged_position / current_price
                    
                    # Calculate actual cost (margin required)
                    margin_required = (position_size * current_price) / self.config['leverage']
                    
                    if margin_required <= self.account['balance']:
                        # Update account balance (only deduct margin)
                        self.account['balance'] -= margin_required
                        
                        # Record the position
                        self.account['positions'][self.symbol] = {
                            'size': position_size,
                            'entry_price': current_price,
                            'stop_loss': current_price * (1 - self.config['stop_loss']/100),
                            'margin': margin_required,
                            'leverage': self.config['leverage']
                        }
                        
                        print(f"\nExecuting BUY:")
                        print(f"Size: {position_size:.8f} {self.symbol}")
                        print(f"Price: ₹{current_price:,.2f}")
                        print(f"Leverage: {self.config['leverage']}x")
                        print(f"Position Value: ₹{(position_size * current_price):,.2f}")
                        print(f"Margin Required: ₹{margin_required:,.2f}")
                        
                        # Save trade to history
                        trade_data = {
                            'timestamp': str(timestamp),
                            'type': 'BUY',
                            'price': current_price,
                            'size': position_size,
                            'leverage': self.config['leverage'],
                            'margin': margin_required,
                            'position_value': position_size * current_price,
                            'balance_after': self.account['balance']
                        }
                        self.account['trade_history'].append(trade_data)
                        self.save_trade_results(trade_data)
                        
                    else:
                        print(f"Insufficient margin. Required: ₹{margin_required:,.2f}, Available: ₹{self.account['balance']:,.2f}")
                
            elif signal == -1:  # Sell signal
                if self.symbol in self.account['positions']:
                    position = self.account['positions'][self.symbol]
                    close_price = position['size'] * current_price
                    entry_value = position['size'] * position['entry_price']
                    
                    # Calculate leveraged P&L
                    raw_profit = close_price - entry_value
                    leveraged_profit = raw_profit * self.config['leverage']
                    
                    # Return margin + profit/loss
                    self.account['balance'] += position['margin'] + leveraged_profit
                    
                    print(f"\nExecuting SELL:")
                    print(f"Size: {position['size']:.8f} {self.symbol}")
                    print(f"Price: ₹{current_price:,.2f}")
                    print(f"Leverage: {self.config['leverage']}x")
                    print(f"P&L: ₹{leveraged_profit:,.2f}")
                    
                    # Save trade to history
                    trade_data = {
                        'timestamp': str(timestamp),
                        'type': 'SELL',
                        'price': current_price,
                        'size': position['size'],
                        'leverage': self.config['leverage'],
                        'profit': leveraged_profit,
                        'balance_after': self.account['balance']
                    }
                    self.account['trade_history'].append(trade_data)
                    self.save_trade_results(trade_data)
                    
                    # Clear the position
                    del self.account['positions'][self.symbol]
            
            # Save updated account state
            self.save_account_state(self.account)
            print(f"Updated Balance: ₹{self.account['balance']:,.2f}")
            
        except Exception as e:
            print(f"Error executing trade: {str(e)}")
    
    def save_trade_log(self, trade):
        """Save individual trade to a separate log file"""
        log_file = 'trade_log.json'
        
        # Load existing logs or create new log array
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                trades = json.load(f)
        else:
            trades = []
        
        # Add new trade
        trades.append(trade)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(trades, f, indent=4)
    
    def calculate_open_position_pnl(self, current_price):
        """Calculate P&L for open positions"""
        if self.symbol in self.account['positions']:
            position = self.account['positions'][self.symbol]
            market_value = position['size'] * current_price
            cost_basis = position['size'] * position['entry_price']
            unrealized_pnl = market_value - cost_basis
            pnl_percentage = (unrealized_pnl / cost_basis) * 100
            
            return {
                'unrealized_pnl': unrealized_pnl,
                'pnl_percentage': pnl_percentage,
                'entry_price': position['entry_price'],
                'current_price': current_price,
                'position_size': position['size']
            }
        return None
    
    def run(self):
        """Main trading loop"""
        print(f"Starting paper trading with ₹{self.account['balance']:,.2f}")
        print(f"Trading {self.symbol} on {self.timeframe} timeframe")
        print(f"Strategy Parameters:")
        print(f"RSI Period: {self.config['rsi_period']}")
        print(f"EMA Fast: {self.config['ema_fast']}")
        print(f"EMA Slow: {self.config['ema_slow']}")
        print(f"ATR Period: {self.config['atr_period']}")
        print(f"Risk Percent: {self.risk_percent}%")
        
        # Calculate sleep time based on timeframe
        sleep_times = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '4h': 14400,
        }
        sleep_time = sleep_times.get(self.timeframe, 3600)
        
        while True:
            try:
                print("\nFetching new market data...")
                self.df = self.get_historical_data()
                
                # Verify we got new data
                current_time = self.df.index[-1]
                print(f"Latest data timestamp: {current_time}")
                
                self.df = self.calculate_indicators(self.df)
                self.df = self.generate_signals(self.df)
                
                # Check for signals
                current_signal = self.df['signal'].iloc[-1]
                current_price = float(self.df['Close'].iloc[-1])
                
                if current_signal != 0:
                    print(f"Signal detected: {'BUY' if current_signal == 1 else 'SELL'}")
                    self.execute_trade(current_signal, current_price, current_time)
                else:
                    print("No trading signal")
                
                # Calculate and display P&L for open positions
                pnl_info = self.calculate_open_position_pnl(current_price)
                if pnl_info:
                    print("\n=== Open Position P&L ===")
                    print(f"Entry Price: ₹{pnl_info['entry_price']:.2f}")
                    print(f"Current Price: ₹{pnl_info['current_price']:.2f}")
                    print(f"Position Size: {pnl_info['position_size']:.8f}")
                    print(f"Unrealized P&L: ₹{pnl_info['unrealized_pnl']:.2f}")
                    print(f"P&L %: {pnl_info['pnl_percentage']:.2f}%")
                    print("========================\n")
                
                print(f"Waiting {self.timeframe} for next check...")
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
    
    def save_trade_results(self, trade_data):
        """Save trade results to JSON file"""
        results_file = 'trade_results.json'
        
        # Load existing results or create new
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
        else:
            results = {
                'trades': [],
                'summary': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_profit': 0,
                    'win_rate': 0
                }
            }
        
        # Add new trade
        results['trades'].append(trade_data)
        
        # Update summary only for SELL trades
        if trade_data['type'] == 'SELL':
            results['summary']['total_trades'] += 1
            profit = trade_data.get('profit', 0)
            if profit > 0:
                results['summary']['winning_trades'] += 1
            results['summary']['total_profit'] += profit
            if results['summary']['total_trades'] > 0:
                results['summary']['win_rate'] = (results['summary']['winning_trades'] / 
                                                results['summary']['total_trades']) * 100
        
        # Save updated results
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)
    
    def check_profit_target(self, df):
        """Check if profit target is hit"""
        if self.symbol in self.account['positions']:
            position = self.account['positions'][self.symbol]
            current_price = df['Close'].iloc[-1]
            entry_price = position['entry_price']
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            return profit_pct >= self.config['profit_target']
        return False
    
    def check_stop_loss(self, df):
        """Check if stop loss is hit"""
        if self.symbol in self.account['positions']:
            position = self.account['positions'][self.symbol]
            current_price = df['Close'].iloc[-1]
            entry_price = position['entry_price']
            loss_pct = ((entry_price - current_price) / entry_price) * 100
            
            # Add trailing stop
            if self.config['trailing_stop']:
                highest_price = max(df['High'].iloc[-20:])  # Look at last 20 candles
                trail_loss_pct = ((highest_price - current_price) / highest_price) * 100
                return loss_pct >= self.config['stop_loss'] or trail_loss_pct >= self.config['stop_loss']
            
            return loss_pct >= self.config['stop_loss']
        return False
    
    def calculate_current_pnl(self, current_price):
        """Calculate current P&L percentage for open position"""
        if self.symbol in self.account['positions']:
            position = self.account['positions'][self.symbol]
            entry_price = position['entry_price']
            return ((current_price - entry_price) / entry_price) * 100
        return 0.0
    