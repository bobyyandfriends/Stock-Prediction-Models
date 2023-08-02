import alpaca_trade_api as tradeapi
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import GetAssetsRequest

# trading_client = TradingClient('PKVRJXN5Z6UZUTX9TJQ5', 't7O4L8Rjwx8oteKifS9N9adoiGPG5jKTpQEMRS1R', paper=True)

# # Get our account information.
# account = trading_client.get_account()
# # Check if our account is restricted from trading.
# if account.trading_blocked:
#     print('Account is currently restricted from trading.')

# # Check how much money we can use to open new positions.
# print('${} is available as buying power.'.format(account.buying_power))
# print(account.positions())
API_KEY = "PKYUGM3AH5XOMZ282TUB"
SECRET_KEY = "JpEIwepalG7aOQ6E1H4s4WB0tgEUJQWMQTxtIMZo"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, SECRET_KEY, APCA_API_BASE_URL)

# Get our position in AAPL.
#aapl_position = api.get_position('AAPL')

# Get a list of all of our positions.
portfolio = api.list_positions()

# Print the quantity of shares for each position.
for position in portfolio:
    print("{} shares of {}".format(position.qty, position.symbol))