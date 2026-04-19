"""
broker.py
"""

from abc import ABC, abstractmethod


class Broker(ABC):
    """Broker facilitates trading"""

    @abstractmethod
    def capital(self, symbol: str) -> float:
        pass

    @abstractmethod
    def position(self, symbol: str) -> float:
        pass

    @abstractmethod
    def value(self, symbol: str) -> float:
        pass

    @abstractmethod
    def buy(self, symbol: str, amount: float) -> float:
        pass

    @abstractmethod
    def sell(self, symbol: str, amount: float) -> float:
        pass
