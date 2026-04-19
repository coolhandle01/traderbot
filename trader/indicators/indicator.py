"""
indicator.py
"""

from abc import ABC, abstractmethod

import pandas as pd

from .signal import Signal


class Indicator(ABC):
    """
    Abstract representation of Market Indicator
    """

    def __init__(self) -> None:
        self.analysis = pd.DataFrame()

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        pass
