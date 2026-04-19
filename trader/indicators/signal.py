"""
signal.py — trading signal enum
"""

from enum import Enum


class Signal(Enum):
    """
    The three possible outputs from any Indicator or Strategy.

    Values are integers so signals can be summed for majority-vote aggregation
    (see DefaultStrategy).
    """

    SELL = -1
    HOLD = 0
    BUY = 1

    # from_str() is not implemented because Signal is only ever produced
    # programmatically by indicators — it is never parsed from user input
    # or persisted to disk.  If serialisation is needed later, use
    # Signal(int(value)) to round-trip via the integer representation.
