from trading_bot import AlgoTrader
# Comment out aggressive config
# from aggressive_config import CONFIG as aggressive_config
# trader = AlgoTrader(aggressive_config)
# trader.run()

# Use conservative trader
from conservative_config import CONFIG as conservative_config
trader = AlgoTrader(conservative_config)
trader.run(continuous_mode=False)  # Run once for GitHub Actions 
