"""
crossover.py — SMA and EMA crossover indicators

Golden cross / death cross strategy:
https://www.investopedia.com/terms/g/goldencross.asp
https://school.stockcharts.com/doku.php?id=technical_indicators:moving_average_crossovers
"""

import pandas as pd

from .indicator import Indicator, Signal


class SMACrossover(Indicator):
    """
    Generates a signal when the fast SMA crosses the slow SMA.

    BUY  (golden cross) — fast crosses above slow: short-term momentum
         is turning bullish relative to the longer-term trend.
    SELL (death cross)  — fast crosses below slow: momentum turning bearish.
    HOLD — no crossover in the last two bars.

    Common pairings: (5, 20), (10, 50), (50, 200).
    """

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
    """
    Generates a signal when the fast EMA crosses the slow EMA.

    Identical logic to SMACrossover but uses exponentially weighted averages,
    which react faster to recent price changes and lag less than a plain SMA.

    BUY  — fast EMA crosses above slow EMA.
    SELL — fast EMA crosses below slow EMA.
    HOLD — no crossover in the last two bars.

    Common pairings: (12, 26) — the same periods used inside MACD.
    """

    def __init__(self, fast: int, slow: int) -> None:
        self.fast = fast
        self.slow = slow

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
