from broker import Broker

class MockBroker(Broker):
    """MockBroker mocks trading"""
    def capital(self, symbol) -> float:
        return 500.0

    def position(self, symbol) -> float:
        return 0.0

    def value(self, symbol):
        return 1.0

    def buy(self, symbol, amount):
        self.current_capital  = 0
        self.current_position = amount
        print(f'bought {self.current_position} shares of {symbol} worth ${amount}')
    
    def sell(self, symbol, amount):
        print(f'sold {self.current_position} shares of {symbol} worth ${amount}')
        self.current_capital  = amount
        self.current_position = 0
