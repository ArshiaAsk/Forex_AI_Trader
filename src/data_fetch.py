import yfinance as yf
import sqlite3 
import pandas as pd
from datetime import datetime


def fetch_yahoo(symbol, interval='15m', period='60d'):
    
    # download data
    df = yf.download(symbol, interval=interval, period=period)
    df.reset_index(inplace=True)
    
    # cleaning dataframe's rows
    df = df.iloc[2:].copy()
    
    # drop Volume columns
    if 'Volume' in df.columns:
        df.drop(columns=['Volume'], inplace=True)
        
    # creating new columns name    
    new_columns = ['Datetime', 'Close', 'High', 'Low', 'Open']
    df.columns = new_columns
    
    # removing empty rows
    df.dropna(inplace=True)
    
    # sorting base on time
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.sort_values('Datetime', inplace=True)
    
    return df


def save_to_db(symbol, df, db_name='forex_data.db'):
    conn = sqlite3.connect(db_name)
    table_name = symbol.replace("=", "_").replace("/", "_")
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    
    
if __name__ == "__main__":
    eur_usd = fetch_yahoo("EURUSD=X", interval="15m", period="60d")
    save_to_db("EURUSD=X", eur_usd)
    print("Data fetch & save in DB form YahooFinance")

