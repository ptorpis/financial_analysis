import yfinance as yf

ticker = yf.Ticker("MSFT")

data = ticker.income_stmt

print(data)