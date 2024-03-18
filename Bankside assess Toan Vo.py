import yfinance as yf
import pandas as pd
import numpy as np


# Define the stock symbols
stock_symbols = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'GOOG', 'META', 'TSLA']

# Define start and end dates
start_date = '2013-01-01'
end_date = '2023-12-31'

# Dictionary to store historical price data for each stock
stock_data = {}

# Retrieve historical price data for each stock
for symbol in stock_symbols:
    stock_data[symbol] = yf.download(symbol, start=start_date, end=end_date)

# Example: Accessing historical price data for MSFT
print("MSFT Historical Data:")
print(stock_data['MSFT'].head())

# Example: Accessing historical price data for AAPL
print("\nAAPL Historical Data:")
print(stock_data['AAPL'].head())


# Function to calculate Double Bollinger Bands
def calculate_dbb(df):
    df['Mid Band'] = df['Adj Close'].rolling(window=20).mean()
    df['20 Day STD'] = df['Adj Close'].rolling(window=20).std()
    df['Upper Band'] = df['Mid Band'] + (2 * df['20 Day STD'])
    df['Lower Band'] = df['Mid Band'] - (2 * df['20 Day STD'])
    return df

# Function to generate buy and sell signals
def generate_signals(df):
    signals = pd.DataFrame(index=df.index)
    signals['Signal'] = 0.0

    # Buy signals
    signals['Signal'][df['Adj Close'] < df['Lower Band']] = 1.0

    # Sell signals
    signals['Signal'][df['Adj Close'] > df['Upper Band']] = -1.0

    return signals

# Apply the Double Bollinger Bands strategy to each stock's historical data
for symbol in stock_symbols:
    stock_data[symbol] = calculate_dbb(stock_data[symbol])
    stock_data[symbol] = pd.concat([stock_data[symbol], generate_signals(stock_data[symbol])], axis=1)

# Example: Displaying the DataFrame with Double Bollinger Bands and signals for MSFT
print("MSFT Historical Data with Double Bollinger Bands and Signals:")
print(stock_data['MSFT'].tail())


# Define initial capital
initial_capital = 10000

# Function to backtest trading signals
def backtest_signals(df):
    capital = initial_capital
    shares_owned = 0
    position_value = 0
    starting_shares = 0
    transactions = []

    for index, row in df.iterrows():
        close_price = row['Adj Close']
        signal = row['Signal']

        # Buy signal
        if signal == 1.0 and capital >= close_price:
            shares_to_buy = int(capital / close_price)
            capital -= shares_to_buy * close_price
            shares_owned += shares_to_buy
            position_value = shares_owned * close_price
            transactions.append(('BUY', index, close_price, shares_to_buy))
            if starting_shares == 0:
                starting_shares = shares_owned

        # Sell signal
        elif signal == -1.0 and shares_owned > 0:
            capital += shares_owned * close_price
            transactions.append(('SELL', index, close_price, shares_owned))
            shares_owned = 0
            position_value = 0

    # Calculate final portfolio value
    final_value = capital + (shares_owned * close_price)
    return final_value, transactions

# Perform backtesting for each stock
backtest_results = {}
for symbol in stock_symbols:
    final_value, transactions = backtest_signals(stock_data[symbol])
    backtest_results[symbol] = {'Final Portfolio Value': final_value, 'Transactions': transactions}

# Display backtesting results
for symbol, result in backtest_results.items():
    print(f"Backtesting results for {symbol}:")
    print(f"Final Portfolio Value: ${result['Final Portfolio Value']:.2f}")
    print("Transactions:")
    for transaction in result['Transactions']:
        print(transaction)
    print()


# Function to compute performance metrics
def compute_metrics(transactions, final_portfolio_value):
    # Calculate total return
    total_return = (final_portfolio_value - initial_capital) / initial_capital

    # Calculate annual return
    start_date = transactions[0][1]
    end_date = transactions[-1][1]
    years = (end_date - start_date).days / 365
    annual_return = (final_portfolio_value / initial_capital) ** (1 / years) - 1

    # Calculate daily returns
    returns = [(trans[3] * trans[2]) for trans in transactions]
    daily_returns = np.diff(returns) / returns[:-1]

    # Calculate annual volatility
    annual_volatility = np.std(daily_returns) * np.sqrt(252)

    # Calculate Sharpe ratio
    risk_free_rate = 0  # Assume risk-free rate is 0 for simplicity
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

    # Calculate Sortino ratio
    downside_returns = np.where(daily_returns < 0, daily_returns, 0)
    sortino_ratio = (annual_return - risk_free_rate) / np.std(downside_returns) * np.sqrt(252)

    # Calculate maximum drawdown
    max_drawdown = 0
    peak = 0
    for ret in returns:
        if ret > peak:
            peak = ret
        elif (peak - ret) / peak > max_drawdown:
            max_drawdown = (peak - ret) / peak

    return {
        'Total Return': total_return,
        'Annual Return': annual_return,
        'Annual Volatility': annual_volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Sortino Ratio': sortino_ratio,
        'Maximum Drawdown': max_drawdown
    }

# Compute performance metrics for each stock
performance_metrics = {}
for symbol, result in backtest_results.items():
    final_portfolio_value = result['Final Portfolio Value']
    transactions = result['Transactions']
    performance_metrics[symbol] = compute_metrics(transactions, final_portfolio_value)

# Display performance metrics
for symbol, metrics in performance_metrics.items():
    print(f"Performance metrics for {symbol}:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    print()