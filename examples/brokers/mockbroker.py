from broker import Broker


class MockBroker(Broker):
    """MockBroker mocks trading"""

    def __init__(self) -> None:
        super().__init__()
        self.current_capital: float = 500.0
        self.current_position: float = 0.0

    def capital(self) -> float:
        return self.current_capital

    def investments(self) -> float:
        return self.current_position

    def position(self, symbol: str) -> float:
        return self.current_position

    def price(self, symbol: str) -> float:
        return 1.0

    def stamp_duty(self, symbol: str) -> float:
        return 0.0

    def fees(self, symbol: str) -> float:
        return 0.0

    def buy(self, symbol: str, amount: float) -> float:
        price = self.price(symbol)
        quantity = amount / price
        self.current_capital -= amount
        self.current_position += quantity
        self._record_buy(symbol, quantity, price)
        print(f"bought {quantity} shares of {symbol} worth ${amount}")
        return quantity

    def sell(self, symbol: str, amount: float) -> float:
        price = self.price(symbol)
        capital_received = amount * price
        self._record_sell(symbol, amount, price)
        print(f"sold {amount} shares of {symbol} worth ${capital_received}")
        self.current_capital += capital_received
        self.current_position = 0.0
        return capital_received
