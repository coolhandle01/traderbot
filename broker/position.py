"""
position.py — lightweight position snapshot helper
"""

import locale

from .broker import Broker
from .stock import Stock


class Position:
    """
    A refreshable snapshot of the current position for a single stock.

    Thin wrapper around broker.position() that formats the value as a
    locale-aware currency string for display purposes.
    """

    def __init__(self) -> None:
        self.position: float = 0.0

    def update(self, broker: Broker, stock: Stock) -> None:
        """Refresh the position from the broker."""
        self.position = broker.position(stock.symbol)

    def __str__(self) -> str:
        return locale.currency(self.position, symbol=True, grouping=True)
