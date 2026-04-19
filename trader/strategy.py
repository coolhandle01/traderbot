"""
strategy.py
"""

from abc import ABC, abstractmethod

import pandas as pd

from .indicators import Indicator, Signal


class Strategy(ABC):
    """
    A Strategy holds a collection of Indicators and aggregates their signals
    into a single BUY / SELL / HOLD decision for a given price history.

    Subclass this and implement `signal()` to define the aggregation logic.
    """

    def __init__(self) -> None:
        super()
        self.indicators: list[Indicator] = []

    def add_indicator(self, indicator: Indicator) -> None:
        self.indicators.append(indicator)

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        """Return a trading signal based on the supplied price history."""
        pass


class DefaultStrategy(Strategy):
    """
    Majority-vote strategy: asks every indicator for a signal and returns
    whichever of BUY or SELL has a strict majority.  HOLD wins ties.

    This is the simplest meaningful aggregation — a starting point you can
    replace with weighted voting, threshold rules, or ML-based logic.
    """

    def signal(self, df: pd.DataFrame) -> Signal:
        signals = [ind.signal(df) for ind in self.indicators]
        buys = sum(1 for s in signals if s == Signal.BUY)
        sells = sum(1 for s in signals if s == Signal.SELL)
        total = len(signals)

        if total == 0:
            return Signal.HOLD
        if buys > total / 2:
            return Signal.BUY
        if sells > total / 2:
            return Signal.SELL
        return Signal.HOLD
