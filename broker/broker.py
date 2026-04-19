"""
broker.py
"""

from abc import ABC, abstractmethod

from .ledger import Receipt, _make_buy_receipt, _make_sell_receipt


class Broker(ABC):
    """Broker facilitates trading"""

    def __init__(self) -> None:
        self.ledger: list[Receipt] = []

    @abstractmethod
    def capital(self) -> float:
        pass

    @abstractmethod
    def investments(self) -> float:
        pass

    @abstractmethod
    def position(self, symbol: str) -> float:
        pass

    @abstractmethod
    def price(self, symbol: str) -> float:
        pass

    @abstractmethod
    def stamp_duty(self, symbol: str) -> float:
        pass

    @abstractmethod
    def fees(self, symbol: str) -> float:
        pass

    @abstractmethod
    def buy(self, symbol: str, amount: float) -> float:
        pass

    @abstractmethod
    def sell(self, symbol: str, amount: float) -> float:
        pass

    def _record_buy(self, symbol: str, quantity: float, price: float) -> Receipt:
        receipt = _make_buy_receipt(
            symbol=symbol,
            quantity=quantity,
            price=price,
            fee_rate=self.fees(symbol),
            tax_rate=self.stamp_duty(symbol),
        )
        self.ledger.append(receipt)
        return receipt

    def _record_sell(self, symbol: str, quantity: float, price: float) -> Receipt:
        receipt = _make_sell_receipt(
            symbol=symbol,
            quantity=quantity,
            price=price,
            fee_rate=self.fees(symbol),
            tax_rate=self.stamp_duty(symbol),
        )
        self.ledger.append(receipt)
        return receipt
