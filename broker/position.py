import locale

from stock import Stock

from broker import Broker


class Position:
    def __init__(self) -> None:
        self.position: float = 0.0

    def update(self, broker: Broker, stock: Stock) -> None:
        self.position = broker.position(stock.symbol)

    def __str__(self) -> str:
        text = locale.currency(self.position, symbol=True, grouping=True)
        return text
