"""
ledger.py — double-entry receipt model for broker transactions
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Entry:
    """One side of a double-entry line."""

    account: str  # e.g. "cash", "securities:AAPL", "fees", "taxes"
    debit: float
    credit: float


@dataclass(frozen=True)
class Receipt:
    """
    An immutable record of a single BUY or SELL transaction.

    Double-entry invariant: sum(e.debit for e in entries) == sum(e.credit for e in entries)
    """

    timestamp: datetime
    action: str  # "BUY" | "SELL"
    symbol: str
    quantity: float  # units transacted
    price: float  # per-unit price
    gross: float  # quantity * price
    fees: float  # broker fees paid (absolute £/$)
    taxes: float  # stamp duty paid (absolute £/$)
    net: float  # cash actually moved (out for BUY, in for SELL)
    entries: tuple[Entry, ...]

    def balanced(self) -> bool:
        total_debit = sum(e.debit for e in self.entries)
        total_credit = sum(e.credit for e in self.entries)
        return abs(total_debit - total_credit) < 1e-9


def _make_buy_receipt(
    symbol: str,
    quantity: float,
    price: float,
    fee_rate: float,
    tax_rate: float,
) -> Receipt:
    gross = quantity * price
    fees = gross * fee_rate
    taxes = gross * tax_rate
    net = gross + fees + taxes  # total cash out
    return Receipt(
        timestamp=datetime.now(),
        action="BUY",
        symbol=symbol,
        quantity=quantity,
        price=price,
        gross=gross,
        fees=fees,
        taxes=taxes,
        net=net,
        entries=(
            Entry(account=f"securities:{symbol}", debit=gross, credit=0.0),
            Entry(account="fees", debit=fees, credit=0.0),
            Entry(account="taxes", debit=taxes, credit=0.0),
            Entry(account="cash", debit=0.0, credit=net),
        ),
    )


def _make_sell_receipt(
    symbol: str,
    quantity: float,
    price: float,
    fee_rate: float,
    tax_rate: float,
) -> Receipt:
    gross = quantity * price
    fees = gross * fee_rate
    taxes = gross * tax_rate
    net = gross - fees - taxes  # cash in after costs
    return Receipt(
        timestamp=datetime.now(),
        action="SELL",
        symbol=symbol,
        quantity=quantity,
        price=price,
        gross=gross,
        fees=fees,
        taxes=taxes,
        net=net,
        entries=(
            Entry(account="cash", debit=net, credit=0.0),
            Entry(account="fees", debit=fees, credit=0.0),
            Entry(account="taxes", debit=taxes, credit=0.0),
            Entry(account=f"securities:{symbol}", debit=0.0, credit=gross),
        ),
    )
