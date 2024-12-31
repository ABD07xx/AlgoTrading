from trading_bot import AlgoTrader
from aggressive_config import CONFIG as aggressive_config

# Initialize and run aggressive trader
trader = AlgoTrader(aggressive_config)
trader.run()

# Comment out conservative trader
# from conservative_config import CONFIG as conservative_config
# trader = AlgoTrader(conservative_config)
# trader.run() 