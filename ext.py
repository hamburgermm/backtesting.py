from datetime import timedelta
from typing import Type, TypedDict, List
from typing_extensions import NotRequired
from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta


def check_time(t, timearr):
    for start_t, exit_t in zip(timearr, timearr[1:]):
        if start_t >= t >= exit_t:
            print(start_t, t, exit_t)


class BacktestArgs(TypedDict):
    data: pd.DataFrame
    strategy: Type[Strategy]
    cash: NotRequired[float]
    commission: NotRequired[float]
    margin: NotRequired[float]
    trade_on_close: NotRequired[bool]
    hedging: NotRequired[bool]
    exclusive_orders: NotRequired[bool]


class BacktestWrapper:
    coins: List[BacktestArgs]

    def __init__(self, coins: List[BacktestArgs]):
        self.coins = coins

    def alpha(self):
        pass

    @staticmethod
    def metric_report(output: pd.Series, interval=timedelta(days=1).total_seconds()) -> List[dict]:
        start = int(output['Start'].timestamp())
        trades_df = output['_trades'].copy()
        trades_df['entry_ts'] = trades_df.apply(lambda x: int(x['EntryTime'].timestamp()), axis=1)
        trades_df['exit_ts'] = trades_df.apply(lambda x: int(x['ExitTime'].timestamp()), axis=1)
        trades_df['time_group'] = trades_df.apply(lambda x: (x['exit_ts'] - start) // interval, axis=1)

        trade_group = trades_df.groupby('time_group')
        results = []
        for key, _ in trade_group:
            df = trade_group.get_group(key)
            time_grp = df.iloc[0]['time_group']
            result = {
                "start_ts": int(start + interval * time_grp),
                "end_ts": int(start + interval * (time_grp + 1)),
                "num_of_trade": len(df),
                "pnl": df['PnL'].sum()
            }
            results.append(result)
        return results

    def run(self):
        outputs = []
        arr = []
        for coin in self.coins:
            _bt = Backtest(**coin)
            _output = _bt.run()
            outputs.append(_output)
            arr.append(_output['Return (Ann.) [%]'])  # dun know what to be input

        np_arr = np.array(arr)
        norm_arr = np_arr / np_arr.sum()
        return {
            "output": outputs,
            "metrics": norm_arr
        }
