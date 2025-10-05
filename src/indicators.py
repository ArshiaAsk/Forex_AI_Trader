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