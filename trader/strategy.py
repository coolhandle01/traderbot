"""
strategy.py
"""
from abc import ABC, abstractmethod
import io
import pickle
import pandas as pd

from indicators import Indicator, Signal
 
class Strategy(ABC):
    """A strategy represents a set of Indicators evaluated in some manner"""
    def __init__(self) -> None:
        super()
        self.indicators = dict()

    def add_indicator(self, name: str, indicator: Indicator) -> None:
        self.indicators[name] = indicator

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        """generate a signal"""
        pass

    @abstractmethod
    def load(self, stream: io.BufferedReader) -> None:
        """save strategy"""
        #pickle.load(self, stream)
        pass
            
    @abstractmethod
    def save(self, stream: io.BufferedWriter) -> None:
        """save strategy"""
        #pickle.dump(self, stream)
        pass
