import schedule
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import yfinance as yf
import numpy as np
import pandas as pd
import time
import sys 
import os
# sys.path.append(os.path.abspath("/Users/benal/StockTrader/Stock-Prediction-Models/agent"))

from agent6 import *

days_ago = datetime.now() - timedelta(days=45)
df = yf.download("GOOG", start=days_ago, end=datetime.now(), interval='1h')

API_KEY = "PK8JAI6R51F7SC86GT4L"
SECRET_KEY = "vIOxUHOwrVZve7kDfnEvijBrQg9cKcoPUedgAqJY"

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


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

# Submitting the order and then printing the returned object
for buy in states_buy:
    if buy > days - 2:
        market_order = trading_client.submit_order(market_order_data_buy)
        for property_name, value in market_order:
            print(f"\"{property_name}\": {value}")
for sell in states_sell:
    if sell > days - 2:
        market_order = trading_client.submit_order(market_order_data_sell)
        for property_name, value in market_order:
            print(f"\"{property_name}\": {value}")


# Schedule the execution to start at 9:30 AM
start_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
current_time = datetime.now()

# If the current time is past 9:30 AM, schedule the first execution for the next day
# if current_time > start_time:
#     start_time += timedelta(days=1)

# Calculate the time difference in seconds between the current time and the scheduled start time
time_difference_start = (start_time - current_time).total_seconds()

# Calculate the time difference in seconds between the current time and 4 PM
end_time = current_time.replace(hour=23, minute=0, second=0, microsecond=0)
time_difference_end = (end_time - current_time).total_seconds()

# Wait until the scheduled start time
#time.sleep(time_difference_start)

# Run the code every 15 minutes until 4 PM
while current_time <= end_time:
    #trial()
    time.sleep(900)  # 900 seconds = 15 minutes
    current_time = datetime.now()


print("Execution has been completed.")