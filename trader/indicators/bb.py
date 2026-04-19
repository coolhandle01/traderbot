"""
Calculate Bollinger Bands
https://www.alpharithms.com/bollinger-bands-590615/
https://www.quantifiedstrategies.com/python-bollinger-band-trading-strategy/
"""

import pandas as pd
from indicator import Indicator, Signal


class BollingerBands(Indicator):
    """
    Calculate Bollinger Bands using Simple Moving Averages
    tested with window = 20, num_std = 2
    """

    def __init__(self, window: int, num_std: float) -> None:
        self.window = window
        self.num_std = num_std

    def signal(self, df: pd.DataFrame) -> Signal:
        # Calculate rolling mean and standard deviation based on SMA20
        df[f"BB_SMA{self.window}"] = df["Close"].rolling(window=self.window).mean()
        df[f"BB_STD{self.window}"] = df["Close"].rolling(window=self.window).std()

        # Calculate Bollinger Bands
        df["BB_H"] = df[f"BB_SMA{self.window}"] + (
            df[f"BB_SMA{self.window}"] * self.num_std
        )
        df["BB_L"] = df[f"BB_SMA{self.window}"] - (
            df[f"BB_SMA{self.window}"] * self.num_std
        )

        # Calculate Signal
        # We sell the price crosses above the upper Bollinger Band
        if df["Close"].iloc[-1] > df["BB_UPPER"].iloc[-1]:
            return Signal.SELL
        # We buy when the closing price is under the lower Bollinger Band
        elif df["Close"].iloc[-1] < df["BB_LOWER"].iloc[-1]:
            return Signal.BUY

        return Signal.HOLD
