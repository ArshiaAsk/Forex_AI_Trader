import sqlite3 
import pandas as pd
import backtrader as bt

DB_NAME = 'forex_data.db'

def load_data(symbol):
    conn = sqlite3.connect(DB_NAME)
    table_name = symbol.replace("=", "_").replace("/", "_")
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    
    if 'Volume' not in df.columns:
        df['Volume'] = 0
    
    return df


class SMAvsEMA(bt.Strategy):
    params = (
        ('sma_period', 50),
        ('ema_period', 20),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close,
                                                     period=self.params.sma_period)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close,
                                                          period=self.params.ema_period)
        
    
    def next(self):
        
        # conditon of buy
        if not self.position and self.sma[0] > self.ema[0]:
            size = self.broker.get_cash() / self.data.close[0]
            self.buy(size=size)
            
        # condition of sell  
        if self.position and self.sma[0] < self.ema[0]:
            self.sell(size = self.position.size)
            
    
if __name__ == "__main__":
    symbol = "EURUSD=X"
    df = load_data(symbol)
    
    # conver data to Backtrader compatible DataFeed
    data = bt.feeds.PandasData(dataname=df)
    
    # create a backtest engine
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    
    # initial capital
    cerebro.broker.setcash(100.0)
    
    # adding strategy
    cerebro.addstrategy(SMAvsEMA)
    
    # size of commission
    cerebro.broker.setcommission(commission=0.0)
    
    print(f"Strat Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.run()
    print(f"End Portfolio Value: {cerebro.broker.getvalue():.2f}")
    
    cerebro.plot()