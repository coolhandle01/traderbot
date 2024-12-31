"""
broker.py
"""
from abc import ABC, abstractmethod

class Broker(ABC):
    """Broker facilitates trading"""
    def __init__(self) -> None:
        pass

    @abstractmethod
    def capital(self, symbol) -> float:
        pass

    @abstractmethod
    def position(self, symbol) -> float:
        pass

    @abstractmethod
    def value(self, symbol) -> float:
        pass

    @abstractmethod
    def buy(self, symbol, amount) -> float:
        pass
    
    @abstractmethod
    def sell(self, symbol, amount) -> float:
        pass
