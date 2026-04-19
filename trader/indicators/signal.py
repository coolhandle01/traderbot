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
