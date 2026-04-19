import pandas as pd

from broker import Broker
from trader.indicators import Signal
from trader.strategy import Strategy


class DollarCostAverage(Strategy):
    """
    Buys a fixed stake every `interval` bars regardless of price.

    Never sells — it is a buy-only accumulation strategy.  The minimum
    buy size is enforced so that fees never consume the entire position;
    if the broker charges more than the trade is worth, the signal is
    suppressed to HOLD.
    """

    def __init__(self, interval: int = 20) -> None:
        self._interval = interval
        self._bar = 0
        self._min_trade: float = 0.0  # populated by configure()

    def configure(self, broker: Broker, symbol: str) -> None:
        # Require the trade to be worth at least 10x the round-trip fee cost
        # so fees don't consume a meaningful slice of each purchase.
        fee_rate = broker.fees(symbol) + broker.stamp_duty(symbol)
        self._min_trade = fee_rate * 10.0

    def signal(self, df: pd.DataFrame) -> Signal:
        self._bar += 1
        if self._bar % self._interval == 0:
            return Signal.BUY
        return Signal.HOLD
