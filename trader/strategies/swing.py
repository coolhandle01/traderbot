import pandas as pd

from broker import Broker
from trader.indicators import Signal
from trader.strategy import Strategy


class Swing(Strategy):
    """
    Buys dips, sells bounces within a rolling price window.

    BUY  when the current close is at least `threshold` below the rolling high
         (the price has dipped — enter the position).
    SELL when the current close is at least `threshold` above the rolling low
         (the price has bounced — take profit).

    `configure()` bumps the threshold to at least the round-trip fee cost so
    the strategy never signals a trade that cannot break even after fees.
    """

    def __init__(self, window: int = 20, threshold: float = 0.05) -> None:
        self._window = window
        self._threshold = threshold

    def configure(self, broker: Broker, symbol: str) -> None:
        round_trip = broker.fees(symbol) * 2 + broker.stamp_duty(symbol)
        # add a small buffer above breakeven
        self._threshold = max(self._threshold, round_trip + 0.005)

    def signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._window:
            return Signal.HOLD

        recent = df["Close"].iloc[-self._window :]
        current = float(df["Close"].iloc[-1])
        rolling_high = float(recent.max())
        rolling_low = float(recent.min())

        if current <= rolling_high * (1.0 - self._threshold):
            return Signal.BUY
        if current >= rolling_low * (1.0 + self._threshold):
            return Signal.SELL
        return Signal.HOLD
