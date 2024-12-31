"""
indicator.py
"""
from abc import ABC, abstractmethod
import io
import pandas as pd
from .signal import Signal

class Indicator(ABC):
    """
    Abstract representation of Market Indicator 
    """
    def __init__(self) -> None:
        self.analysis = pd.DataFrame

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        """
        The Signal from this Indicator.
        """
        pass

    @abstractmethod
    def load(self, stream: io.BufferedReader) -> None:
        """
        Load this Indicator from file.
        """
        pass

    @abstractmethod
    def save(self, stream: io.BufferedWriter) -> None:
        """
        Save this Indicator to file.
        """
        pass
