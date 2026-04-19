"""
trader.py
"""

import pandas as pd

from broker import Broker, Stock, StockAnalysis

from .indicators import Signal
from .state import TraderState
from .strategy import Strategy


class Trader:
    """Trade a symbol at a broker"""

    def __init__(self, stock: Stock, broker: Broker, strat: Strategy) -> None:
        self.stock = stock
        self.broker = broker
        self.strategy = strat
        self.state = TraderState.WAITING
        self.analysis = self.stock.copy()

        self.position = self.broker.position(self.stock.symbol)
        self.capital = self.broker.capital()

        self.initial_capital = self.capital
        self.trade_max_bet = self.initial_capital * 0.1
        self.trade_min_profit = self.trade_max_bet * 0.1

        self.stock_analysis = StockAnalysis(self.stock)

    def evaluate(self) -> Signal:
        """analyse the history with the given strategy"""
        self.analysis = pd.concat([self.analysis, self.stock.tail()])
        return self.strategy.signal(self.analysis)

    def buy(self) -> None:
        """use capital to buy a position from the broker"""
        if self.capital <= 0.0:
            raise ValueError("cannot buy: no capital available")

        self.state = TraderState.BUYING

        tender = (
            self.capital if self.trade_max_bet > self.capital else self.trade_max_bet
        )

        self.position += self.broker.buy(self.stock.symbol, tender)
        self.capital -= tender

        self.state = TraderState.HOLDING

    def sell(self) -> None:
        """sell the position to the broker for capital"""
        if self.position <= 0.0:
            raise ValueError("cannot sell: no position held")

        self.state = TraderState.SELLING

        gross = self.position * self.broker.price(self.stock.symbol)
        tax = self.broker.stamp_duty(self.stock.symbol)
        fees = self.broker.fees(self.stock.symbol)
        net = gross - ((gross * tax) + (gross * fees))

        if net > self.trade_min_profit:
            self.capital += self.broker.sell(self.stock.symbol, self.position)
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
        print(
            f"changed position on {self.stock.symbol}: ${self.capital}: {self.position}"
        )
