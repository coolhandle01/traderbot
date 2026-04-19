"""
strategy.py
"""

from abc import ABC, abstractmethod

import pandas as pd

from broker import Broker

from .indicators import Indicator, Signal


class Strategy(ABC):
    """
    Aggregates one or more signals into a single BUY / SELL / HOLD decision.

    Subclass and implement `signal()`.  Override `configure()` to receive
    broker fee context before the first trade.
    """

    def configure(self, broker: Broker, symbol: str) -> None:  # noqa: B027
        """Called by Trader after construction; override to receive fee context."""

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        """Return a trading signal based on the supplied price history."""
        pass


class DefaultStrategy(Strategy):
    """
    Majority-vote strategy: asks every indicator for a signal and returns
    whichever of BUY or SELL has a strict majority.  HOLD wins ties.
    """

    def __init__(self) -> None:
        self.indicators: list[Indicator] = []

    def add_indicator(self, indicator: Indicator) -> None:
        self.indicators.append(indicator)

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
