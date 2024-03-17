import datetime
import numpy as np
import pandas_datareader.data as web
import yfinance as yfin

yfin.pdr_override()

def get_stock_data(num_stocks=7, start="2013-01-01", end="2023-12-31"):
  stocks = {}
  for i in range(num_stocks):
    while True:
      ticker = input(f"Enter ticker symbol for stock {i+1} (or 'q' to quit): ")
      if ticker.lower() == 'q':
        return stocks  # Early exit if user enters 'q'

      try:
        # Download data for the current ticker within the specified date range
        data = web.DataReader(ticker, start=start, end=end)
        stocks[ticker] = data
        break  # Exit inner loop if download successful
      except (web.DataReader, KeyError):
        print(f"Invalid ticker symbol: {ticker}. Please try again.")

  return stocks

if __name__ == "__main__":
  stock_data = get_stock_data()

  if stock_data:
    print("Successfully downloaded data for the following stocks:")
    for ticker, data in stock_data.items():
      print(f"- {ticker}")
  else:
    print("No stocks downloaded.")

data.head()