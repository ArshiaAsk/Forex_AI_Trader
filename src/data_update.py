import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_NAME = 'forex_data.db'
 
def fetch_recent_data(symbol, interval="15m", lookback_days=5):
    period = f"{lookback_days}d"
    df = yf.download(symbol, interval=interval, period=period)
    df.reset_index(inplace=True)
    return df


def update_db(symbol, interval="15m", lookback_days=5):
    conn = sqlite3.connect(DB_NAME)
    table_name = symbol.replace("=", "_").replace("/", "_")
    
    try:
        old_df = pd.read_sql(f"SELECT * FROM'{table_name}'", conn)
        old_df['Datetime'] = pd.to_datetime(old_df['Datetime'])
        
    except Exception:
        old_df = pd.DataFrame()
        
    
    new_df = fetch_recent_data(symbol, interval=interval, lookback_days=lookback_days)
    
    
    if not old_df.empty:
        combined_df = pd.concat([old_df, new_df])
        combined_df.drop_duplicates(subset=['Datetime'], keep='last', inplace=True)
        combined_df.sort_values('Datetime', inplace=True)
    else:
        combined_df = new_df
        
    combined_df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"Table {table_name} has {len(combined_df)} new record")
    
    
if __name__ == "__mian__":
    update_db("EURUSD=X", interval='15m', lookback_days=5)
    
print("done")