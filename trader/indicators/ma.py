"""
ma.py — Simple Moving Average indicator
https://www.alpharithms.com/simple-moving-average-sma-python-421912/
"""

import pandas as pd

from .indicator import Indicator, Signal


class SimpleMovingAverage(Indicator):
    """
    Adds a rolling SMA column to the DataFrame but always returns HOLD.

    SMA is a chart indicator used to smooth price data and identify trend
    direction; it does not generate signals on its own.  Pair it with a
    crossover indicator (SMACrossover) or use it as a visual reference in
    the Report.

    Tested with window = 5, 10, 20 (common short/medium/long-term periods).
    """

    def __init__(self, window: int) -> None:
        self.window = window

    def signal(self, df: pd.DataFrame) -> Signal:
        df[f"SMA{str(self.window)}"] = df["Close"].rolling(window=self.window).mean()
        return Signal.HOLD
