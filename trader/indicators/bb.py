"""
Calculate Bollinger Bands
https://www.alpharithms.com/bollinger-bands-590615/
https://www.quantifiedstrategies.com/python-bollinger-band-trading-strategy/
"""

import pandas as pd

from .indicator import Indicator, Signal


class BollingerBands(Indicator):
    """
    Calculate Bollinger Bands using Simple Moving Averages
    tested with window = 20, num_std = 2
    """

    def __init__(self, window: int, num_std: float) -> None:
        self.window = window
        self.num_std = num_std

    def signal(self, df: pd.DataFrame) -> Signal:
        sma = df["Close"].rolling(window=self.window).mean()
        std = df["Close"].rolling(window=self.window).std()

        # Upper and lower bands are SMA ± (num_std standard deviations)
        df["BB_H"] = sma + (std * self.num_std)
        df["BB_L"] = sma - (std * self.num_std)

        last_close = df["Close"].iloc[-1]

        # Price breaking above the upper band signals overbought → sell
        if last_close > df["BB_H"].iloc[-1]:
            return Signal.SELL
        # Price breaking below the lower band signals oversold → buy
        if last_close < df["BB_L"].iloc[-1]:
            return Signal.BUY

        return Signal.HOLD
