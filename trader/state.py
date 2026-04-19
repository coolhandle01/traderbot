"""
state.py — Trader lifecycle states
"""

from enum import Enum


class TraderState(Enum):
    """
    Tracks the current phase of a Trader's decision cycle.

    WAITING  — no position held; evaluating whether to enter.
    BUYING   — buy order in progress.
    HOLDING  — position held; evaluating whether to exit.
    SELLING  — sell order in progress.
    """

    WAITING = 0
    BUYING = 1
    HOLDING = 2
    SELLING = 3
