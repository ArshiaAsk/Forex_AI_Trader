import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import ta

DB_NAME = 'forex_data.db'

def load_data(symbol, interval='15m'):
    conn = sqlite3.connect(DB_NAME)
    table_name = symbol.replace("=", "_").replace("/", "_")
    df = pd.read_sql(f"SELECT * FROM '{table_name}'", conn)
    conn.close()
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.sort_values('Datetime', inplace=True)
    return df


def add_indicators(df):
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()
    
    return df


def plot_price_with_indicators(df, symbol):
    plt.figure(figsize=(12,6))
    plt.plot(df['Datetime'], df['Close'], label='Close Price', color='blue')
    plt.plot(df['Datetime'], df['SMA_20'], label='SMA 20', color='red')
    plt.plot(df['Datetime'], df['EMA_20'], label='EMA 20', color='green')
    plt.title(f"{symbol} Price with SMA & EMA")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()
    
    
def save_features(df, symbol, interval='15m'):
    conn = sqlite3.connect(DB_NAME)
    table_name = f"{symbol.replace("=", "_").replace("/", "_")}_features_{interval}"
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"{table_name} Data with Indicators saved")
    
    
if __name__ == "__main__":
    symbol = "EURUSD=X"
    interval = "15m"
    
    df = load_data(symbol, interval)
    print(f"Data loaded: {len(df)} rows")
    
    df = add_indicators(df)
    plot_price_with_indicators(df, symbol)
    save_features(df, symbol, interval)
