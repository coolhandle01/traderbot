"""
trader.py
"""

import pandas as pd
from indicators import Signal
from state import TraderState
from strategy import Strategy

from broker import Broker, Stock


class Trader:
    """Trade a symbol at a broker"""

    def __init__(self, stock: Stock, broker: Broker, strat: Strategy) -> None:
        self.position = 0.0
        self.capital = 0.0
        self.state = TraderState.WAITING
        self.stock = stock
        self.broker = broker
        self.strategy = strat
        self.analysis = self.stock.copy()

        self.position = self.broker.position(self.stock.symbol)
        self.capital = self.broker.capital(self.stock.symbol)

    def evaluate(self) -> Signal:
        """analyse the history with the given strategy"""
        self.analysis = pd.concat([self.analysis, self.stock.tail()])
        return self.strategy.signal(self.analysis)

    def buy(self) -> None:
        """use capital to buy a position from the trader"""
        self.state = TraderState.BUYING

        self.position = self.broker.buy(self.stock.symbol, self.capital)
        self.capital = 0

        self.state = TraderState.HOLDING

    def sell(self) -> None:
        """sell the position to the broker for capital"""
        self.state = TraderState.SELLING

        self.capital = self.broker.sell(self.stock.symbol, self.position)
        self.position = 0

        self.state = TraderState.WAITING

    def trade(self) -> None:
        """evaluate the stock and make a decision on whether to change the position"""
        # TODO: https://helpcentre.trading212.com/hc/en-us/articles/11471996799517-What-are-the-fees-in-the-Invest-and-ISAs
        match self.evaluate():
            case Signal.BUY:
                if self.capital > 0.0:
                    self.buy()
            case Signal.SELL:
                if self.position > 0.0:
                    self.sell()
            case Signal.HOLD:
                pass
            case _:
                pass
        print(
            f"changed position on {self.stock.symbol}: ${self.capital}: {self.position}"
        )
