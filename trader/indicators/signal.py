"""
signal.py
"""

from enum import Enum


class Signal(Enum):
    """
    Signals are produced by Indicators
    """

    SELL = -1
    HOLD = 0
    BUY = 1

    # @staticmethod
    # def from_str(value: str):
    #    match value:
    #        case 'Signal.SELL': return Signal.SELL
    #        case 'Signal.HOLD': return Signal.HOLD
    #        case 'Signal.BUY':  return Signal.BUY
    #        case _:
    #            raise ValueError(f'{value} is not a valid Signal')
