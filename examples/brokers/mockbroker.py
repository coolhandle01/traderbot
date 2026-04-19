from broker import Broker


class MockBroker(Broker):
    """MockBroker mocks trading"""

    def __init__(self) -> None:
        self.current_capital: float = 500.0
        self.current_position: float = 0.0

    def capital(self, symbol: str) -> float:
        return self.current_capital

    def position(self, symbol: str) -> float:
        return self.current_position

    def value(self, symbol: str) -> float:
        return 1.0

    def buy(self, symbol: str, amount: float) -> float:
        self.current_capital = 0.0
        self.current_position = amount
        print(f"bought {self.current_position} shares of {symbol} worth ${amount}")
        return self.current_position

    def sell(self, symbol: str, amount: float) -> float:
        print(f"sold {self.current_position} shares of {symbol} worth ${amount}")
        self.current_capital = amount
        self.current_position = 0.0
        return self.current_capital
