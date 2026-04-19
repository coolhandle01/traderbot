import locale

from .broker import Broker
from .stock import Stock


class Position:
    def __init__(self) -> None:
        self.position: float = 0.0

    def update(self, broker: Broker, stock: Stock) -> None:
        self.position = broker.position(stock.symbol)

    def __str__(self) -> str:
        text = locale.currency(self.position, symbol=True, grouping=True)
        return text
