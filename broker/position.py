import locale

from stock import Stock
from broker import Broker

class Position:
    def __init__():
        pass

    def update(self, broker: Broker, stock: Stock):
        self.position = broker.position(stock.symbol)

    def __str__(self) -> str:
        # Format a number as a currency string
        value = self.position.value
        text = locale.currency(value, symbol=True, grouping=True)
        return text