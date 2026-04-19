import pandas as pd

from trader.indicators import Signal
from trader.strategy import Strategy


class BuyAndHold(Strategy):
    """
    Buys on the first signal and holds indefinitely.

    The canonical passive benchmark: one entry, no exits, zero ongoing
    transaction costs.  Use this as the floor every active strategy must beat.
    """

    def __init__(self) -> None:
        self._bought = False

    def signal(self, df: pd.DataFrame) -> Signal:
        if not self._bought:
            self._bought = True
            return Signal.BUY
        return Signal.HOLD
