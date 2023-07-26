from datetime import datetime, time, timedelta
import yfinance as yf
import pandas as pd


# List of holidays (you can customize this list based on your region)
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
    # Add more holidays as needed
]

def is_nasdaq_trading_hours():
    current_time = datetime.now().time()
    start_time = time(9, 30)  # NASDAQ opening time
    end_time = time(16, 0)   # NASDAQ closing time

    return start_time <= current_time <= end_time

def is_trading_day(date):
    return date.weekday() < 5 and date.strftime("%Y-%m-%d") not in holidays

def scrape_nasdaq_stock_data(symbol, start_date, end_date):
    # Check if it's NASDAQ trading hours
    if not is_nasdaq_trading_hours():
        print("NASDAQ market is currently closed. Data scraping will not be performed.")
        return

    # Convert start_date and end_date strings to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start_date

    while current_date <= end_date:
        if is_trading_day(current_date):
            days_ago = datetime.now() - timedelta(days=45)
            df = yf.download("GOOG", start=days_ago, end=datetime.now(), interval='1h')

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
    trial()
    time.sleep(3600)  # 900 seconds = 15 minutes
    current_time = datetime.now()


print("Execution has been completed.")