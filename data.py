import yfinance as yf
from datetime import datetime, time as dt_time, timedelta
import csv
import time

# List of holidays (U.S. Stock Market Holiday Schedule for 2023)
holidays = [
    "2023-01-02",  # New Year's Day
    "2023-01-16",  # Martin Luther King, Jr. Day
    "2023-02-20",  # Presidents Day
    "2023-04-07",  # Good Friday
    "2023-05-29",  # Memorial Day
    "2023-06-19",  # Juneteenth Holiday
    "2023-07-04",  # Independence Day
    "2023-09-04",  # Labor Day
    "2023-11-23",  # Thanksgiving Day
    "2023-12-25",  # Christmas Day
]

def is_nasdaq_trading_hours():
    current_time = datetime.now().time()
    start_time = dt_time(9, 30)  # NASDAQ opening time
    end_time = dt_time(16, 0)   # NASDAQ closing time

    return start_time <= current_time <= end_time

def is_trading_day(date):
    return date.weekday() < 5 and date.strftime("%Y-%m-%d") not in holidays

def scrape_nasdaq_stock_data(symbol, start_date, end_date, data_interval, output_file):
    # Check if it's NASDAQ trading hours
    if not is_nasdaq_trading_hours():
        print("NASDAQ market is currently closed. Data scraping will not be performed.")
        return

    # Convert start_date and end_date strings to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start_date

    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"])  # Write header

        while current_date <= end_date:
            if is_trading_day(current_date):
                data = yf.download(symbol, start=current_date, end=current_date, interval=data_interval)
                if not data.empty:
                    date = current_date.strftime("%Y-%m-%d")
                    open_price = data["Open"].values[0]
                    high_price = data["High"].values[0]
                    low_price = data["Low"].values[0]
                    close_price = data["Close"].values[0]
                    adj_close_price = data["Adj Close"].values[0]
                    volume = data["Volume"].values[0]
                    csvwriter.writerow([date, open_price, high_price, low_price, close_price, adj_close_price, volume])  # Write data to CSV

            # Move to the next day
            current_date += timedelta(days=1)

            # Sleep for 15 minutes before the next iteration
            time.sleep(900)  # 15 minutes in seconds
# Example usage
symbol = "AAPL"
start_date = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")
data_interval ='1h'
output_file = f"{symbol}_historical_prices.csv"

scrape_nasdaq_stock_data(symbol, start_date, end_date, data_interval, output_file)
