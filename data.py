import yfinance as yf
import csv
import datetime

# Define the stock symbol and date range
symbol = "AAPL"  # Example stock symbol (Apple Inc.)
start_date = "2022-01-01"  # Example start date
end_date = "2022-12-31"  # Example end date


today = datetime.datetime.now()
end_date = today
#print("Today is " + str(today.strftime("%b-%d-%Y")))
print(end_date)
fifteen_years_ago = today - datetime.timedelta(days=15*365)
start_date = fifteen_years_ago
#print("The day fifteen years ago was " + str(fifteen_years_ago.strftime("%b-%d-%Y")))
print(start_date)

# Fetch historical stock price data from Yahoo Finance
data = yf.download(symbol, start=start_date, end=end_date)

# Create a CSV file and write the data into it
csv_filename = f"{symbol}_historical_prices.csv"

with open(csv_filename, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Date", "Close Price"])  # Write the header row

    # Iterate over the data and extract the date and closing price
    for index, row in data.iterrows():
        date = index.strftime("%Y-%m-%d")
        close_price = row["Close"]
        writer.writerow([date, close_price])

print(f"Data has been successfully saved to {csv_filename}.")
