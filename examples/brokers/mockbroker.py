from broker import Broker


class MockBroker(Broker):
    """MockBroker mocks trading"""

    def __init__(self) -> None:
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
        self.current_capital -= amount
        self.current_position += amount
        print(f"bought {self.current_position} shares of {symbol} worth ${amount}")
        return self.current_position

    def sell(self, symbol: str, amount: float) -> float:
        capital_received = amount * self.price(symbol)
        print(f"sold {self.current_position} shares of {symbol} worth ${capital_received}")
        self.current_capital += capital_received
        self.current_position = 0.0
        return capital_received
