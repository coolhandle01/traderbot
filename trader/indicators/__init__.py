"""
Trader
"""

from .bb import BollingerBands
from .crossover import EMACrossover, SMACrossover
from .indicator import Indicator
from .ma import SimpleMovingAverage
from .macd import MACD
from .rsi import ResidualStrengthIndex
from .signal import Signal
from .so import StochasticOscillation

__all__ = [
    "Signal",
    "Indicator",
    "BollingerBands",
    "SimpleMovingAverage",
    "SMACrossover",
    "EMACrossover",
    "MACD",
    "ResidualStrengthIndex",
    "StochasticOscillation",
]
