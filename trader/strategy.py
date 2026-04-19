"""
strategy.py
"""

from abc import ABC, abstractmethod

import pandas as pd

from .indicators import Indicator, Signal


class Strategy(ABC):
    """A strategy represents a set of Indicators evaluated in some manner"""

    def __init__(self) -> None:
        super()
        self.indicators: dict[str, Indicator] = {}

    def add_indicator(self, name: str, indicator: Indicator) -> None:
        self.indicators[name] = indicator

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        pass
