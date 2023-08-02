from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG, EURUSD
from ext import BacktestWrapper, BacktestArgs
import pandas as pd


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


if __name__ == '__main__':
    coin1: BacktestArgs = {"data": GOOG, "strategy": SmaCross, "cash": 10000, "commission": .002,
                           "exclusive_orders": True}

    coin2: BacktestArgs = {"data": EURUSD, "strategy": SmaCross, "cash": 10000, "commission": .002,
                           "exclusive_orders": True}

    bt = BacktestWrapper([coin1, coin2])
    r = bt.run()
    out = r['output']
    for i in out:
        df = pd.json_normalize(bt.metric_report(i))
        print(df)
