import schedule
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import alpaca_trade_api as tradeapi
import yfinance as yf
import numpy as np
import pandas as pd
import time
import sys 
import os
# sys.path.append(os.path.abspath("/Users/benal/StockTrader/Stock-Prediction-Models/agent"))
from useable_agent.agent6 import *


# Schedule the execution to start at 9:30 AM
start_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
current_time = datetime.now()


# Calculate the time difference in seconds between the current time and 4 PM
end_time = current_time.replace(hour=23, minute=0, second=0, microsecond=0)
while current_time <= end_time:
    days_ago = datetime.now() - timedelta(days=45)
    df = yf.download("GOOG", start=days_ago, end=datetime.now(), interval='1h')

    API_KEY = "PKYUGM3AH5XOMZ282TUB"
    SECRET_KEY = "JpEIwepalG7aOQ6E1H4s4WB0tgEUJQWMQTxtIMZo"

    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    states_buy, states_sell, total_gains, invest, days = step(df)
    print(states_buy)

    # # Getting account information and printing it
    # account = trading_client.get_account()
    # for property_name, value in account:
    #   print(f"\"{property_name}\": {value}")

    # Setting parameters for our buy order
    market_order_data_buy = MarketOrderRequest(
                        symbol="GOOG",
                        qty=1,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.GTC
                    )
    market_order_data_sell = MarketOrderRequest(
                        symbol="GOOG",
                        qty=1,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.GTC
                    )

    #Get's the positions
    APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
    api = tradeapi.REST(API_KEY, SECRET_KEY, APCA_API_BASE_URL)

    # Get our position in AAPL.
    #aapl_position = api.get_position('GOOG')

    # Get a list of all of our positions.
    portfolio = api.list_positions()

    amount = 0

    # Print the quantity of shares for each position.
    for position in portfolio:
        if position.symbol == "GOOG":
            amount = position.qty

    # Submitting the order and then printing the returned object
    for buy in states_buy:
        if buy > days - 1:
            market_order = trading_client.submit_order(market_order_data_buy)
            for property_name, value in market_order:
                print(f"\"{property_name}\": {value}")
    for sell in states_sell:
        if sell > days - 1 and amount > 0:
            market_order = trading_client.submit_order(market_order_data_sell)
            for property_name, value in market_order:
                print(f"\"{property_name}\": {value}")

    # Run the code every 15 minutes until 4 PM
    time.sleep(3600)  # 900 seconds = 15 minutes
    current_time = datetime.now()


print("Execution has been completed.")