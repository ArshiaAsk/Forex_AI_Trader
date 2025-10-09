import backtrader as bt
import pandas as pd
import sqlite3


DB_NAME = 'forex_data.db'
TABLE_NAME = 'EURUSD_X_1h'


class SmaEmaCross(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('ema_period', 20),
    )
    
    def __init__(self):
        sma = bt.ind.SMA(period=self.params.sma_period)
        ema = bt.ind.EMA(period=self.params.ema_period)
        self.crossover = bt.ind.CrossOver(sma, ema)
        
    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.sell()
                

def load_data_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    
    if 'Volume' not in df.columns:
        df['Volume'] = 0.0
        
    return bt.feeds.PandasData(dataname=df)


if __name__ == "__main__":
    data = load_data_from_db()
    
    cerebro = bt.Cerebro(optreturn=False)
    cerebro.adddata(data)
    
    cerebro.optstrategy(
        SmaEmaCross,
        sma_period=range(5, 51, 5),
        ema_period=range(5, 51, 5),
    )
    
    cerebro.broker.setcash(100.0)
    cerebro.broker.setcommission(commission=0.0002)
    
    results = cerebro.run()
    
    best = sorted(results, key=lambda x: x[0].broker.getvalue(), reverse=True)[:10]
    
    for start in best:
        val = start[0].broker.getvalue()
        print(f"SMA={start[0].params.sma_period}, EMA={start[0].params.ema_period} => Final Value: {val:.2f}")