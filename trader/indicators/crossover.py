"""
crossover.py
"""

import pandas as pd

from .indicator import Indicator, Signal


class SMACrossover(Indicator):
    """Generates BUY when fast SMA crosses above slow SMA, SELL when it crosses below."""

    def __init__(self, fast: int, slow: int) -> None:
        self.fast = fast
        self.slow = slow

    def signal(self, df: pd.DataFrame) -> Signal:
        fast_col = f"SMA{self.fast}"
        slow_col = f"SMA{self.slow}"
        df[fast_col] = df["Close"].rolling(window=self.fast).mean()
        df[slow_col] = df["Close"].rolling(window=self.slow).mean()

        if len(df) < 2:
            return Signal.HOLD

        prev_fast, curr_fast = df[fast_col].iloc[-2], df[fast_col].iloc[-1]
        prev_slow, curr_slow = df[slow_col].iloc[-2], df[slow_col].iloc[-1]

        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return Signal.BUY
        if prev_fast >= prev_slow and curr_fast < curr_slow:
            return Signal.SELL
        return Signal.HOLD


class EMACrossover(Indicator):
    """Generates BUY when fast EMA crosses above slow EMA, SELL when it crosses below."""

    def __init__(self, fast: int, slow: int, overbought: float = 70, oversold: float = 30) -> None:
        self.fast = fast
        self.slow = slow
        self.overbought = overbought
        self.oversold = oversold

    def signal(self, df: pd.DataFrame) -> Signal:
        fast_col = f"EMA{self.fast}"
        slow_col = f"EMA{self.slow}"
        df[fast_col] = df["Close"].ewm(span=self.fast, adjust=False).mean()
        df[slow_col] = df["Close"].ewm(span=self.slow, adjust=False).mean()

        if len(df) < 2:
            return Signal.HOLD

        prev_fast, curr_fast = df[fast_col].iloc[-2], df[fast_col].iloc[-1]
        prev_slow, curr_slow = df[slow_col].iloc[-2], df[slow_col].iloc[-1]

        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return Signal.BUY
        if prev_fast >= prev_slow and curr_fast < curr_slow:
            return Signal.SELL
        return Signal.HOLD
