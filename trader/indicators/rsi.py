"""
rsi.py
"""

import math

import pandas as pd

from .indicator import Indicator, Signal


class ResidualStrengthIndex(Indicator):
    """
    Calculate Relative Strength Index
    tested with window = 14
    https://www.alpharithms.com/relative-strength-index-rsi-in-python-470209/
    """

    def __init__(self, window: int, overbought: float, oversold: float) -> None:
        self.window = window
        self.overbought = overbought
        self.oversold = oversold

    def signal(self, df: pd.DataFrame) -> Signal:
        # calculate the price delta
        diff = df["Close"].diff()

        # calculate gains and losses
        df["gain"] = diff.clip(lower=0).round(2)
        df["loss"] = diff.clip(upper=0).abs().round(2)

        # Get WMS averages

        # SMA?
        df["avg_gain"] = (
            df["gain"]
            .rolling(window=self.window, min_periods=self.window)
            .mean()[: self.window + 1]
        )
        df["avg_loss"] = (
            df["loss"]
            .rolling(window=self.window, min_periods=self.window)
            .mean()[: self.window + 1]
        )

        # Calculate EMA
        # Welles Wilder's Smoothing Method
        # TODO: 'Some modern approaches use an alpha value of `2 / period + 1`'

        # Wilder smoothing: each bar's average = (prev_avg × (window-1) + current) / window
        for i in range(len(df) - self.window - 1):
            j = i + self.window
            k = i + self.window + 1
            df.loc[df.index[k], "avg_gain"] = (
                df["avg_gain"].iloc[j] * (self.window - 1) + df["gain"].iloc[k]
            ) / self.window
            df.loc[df.index[k], "avg_loss"] = (
                df["avg_loss"].iloc[j] * (self.window - 1) + df["loss"].iloc[k]
            ) / self.window

        # Calculate RS Values
        df["RS"] = df["avg_gain"] / df["avg_loss"]
        df["RSI%"] = 100 - (100 / (1.0 + df["RS"]))

        # this is probably crude:
        # A very general trading strategy for the RSI is to
        # sell when the price is above the overbought threshold and
        # buy when it’s below the oversold threshold
        if math.isnan(df["RSI%"].iloc[-1]):
            return Signal.HOLD

        # Overbought status
        if df["RSI%"].iloc[-1] > self.overbought:
            # sell
            return Signal.SELL
        # Oversold status
        elif df["RSI%"].iloc[-1] < self.oversold:
            # buy
            return Signal.BUY
        # Something in the middle
        else:
            return Signal.HOLD
