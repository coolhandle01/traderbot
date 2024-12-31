"""
ma.py
"""
import pandas as pd
from indicator import Indicator, Signal

class SimpleMovingAverage(Indicator):
    def __init__(self, window: int) -> None:
        self.window=window

    def signal(self, df: pd.DataFrame) -> Signal:
        df[f'SMA{str(self.window)}'] = df['Close'].rolling(window=self.window).mean()
        return Signal.HOLD
