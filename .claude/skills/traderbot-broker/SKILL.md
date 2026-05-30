---
name: traderbot-broker
description: The Broker ABC contract (capital, position, price, fees, stamp_duty, buy, sell) and the double-entry ledger receipts that record every transaction. Mock brokers backtest, live brokers (examples/) execute. Load before editing broker/broker.py, broker/ledger.py, broker/position.py, or any broker under examples/brokers/.
---

# Broker and ledger

A `Broker` is the boundary between the trading logic and money - whether
simulated (`MockBroker`, for backtests) or real (`Trading212Broker`, hitting a
live API). Every implementation honours the same abstract contract, and every
buy/sell it executes is recorded as a balanced double-entry receipt.

## The Broker ABC contract

`broker/broker.py` declares the eight abstract methods every broker implements:

```python
class Broker(ABC):
    def __init__(self) -> None:
        self.ledger: list[Receipt] = []

    @abstractmethod
    def capital(self) -> float: ...       # uninvested cash
    @abstractmethod
    def investments(self) -> float: ...   # value currently invested
    @abstractmethod
    def position(self, symbol: str) -> float: ...  # units held of symbol
    @abstractmethod
    def price(self, symbol: str) -> float: ...     # current per-unit price
    @abstractmethod
    def stamp_duty(self, symbol: str) -> float: ...  # tax RATE (fraction)
    @abstractmethod
    def fees(self, symbol: str) -> float: ...        # fee RATE (fraction)
    @abstractmethod
    def buy(self, symbol: str, amount: float) -> float: ...   # returns units bought
    @abstractmethod
    def sell(self, symbol: str, amount: float) -> float: ...  # returns cash received
```

Watch the units, because the `Trader` depends on them:

- `fees()` and `stamp_duty()` return **rates** (fractions like `0.0`, not
  absolute currency). The `Trader` and the ledger multiply them by the gross.
- `buy(symbol, amount)` takes an **amount of cash to spend** and returns the
  **quantity of units** acquired.
- `sell(symbol, amount)` takes a **quantity of units** to sell and returns the
  **cash received**.

A new method on the ABC must be `@abstractmethod` and implemented by both
`MockBroker` and `Trading212Broker` in the same change, or one of them breaks at
instantiation.

## Record every transaction through the ledger helpers

`Broker` provides `_record_buy()` / `_record_sell()`, which build a `Receipt`
via `_make_buy_receipt` / `_make_sell_receipt` and append it to `self.ledger`.
A concrete broker calls these from inside its `buy()` / `sell()` so the audit
trail stays complete:

```python
def buy(self, symbol: str, amount: float) -> float:
    price = self.price(symbol)
    quantity = amount / price
    self.current_capital -= amount
    self.current_position += quantity
    self._record_buy(symbol, quantity, price)   # ledger entry
    return quantity
```

Never mutate `self.ledger` directly or hand-build a `Receipt` - go through the
helpers so the double-entry construction stays in one place.

## The double-entry invariant

`broker/ledger.py` models each transaction as an immutable `Receipt` made of
`Entry` lines (account, debit, credit). The invariant, stated on the `Receipt`
docstring and checked by `balanced()`:

```
sum(debit for entries) == sum(credit for entries)
```

`Receipt` and `Entry` are `@dataclass(frozen=True)` - immutable on purpose, so a
recorded transaction cannot be edited after the fact. `_make_buy_receipt`
computes `net = gross + fees + taxes` (total cash out) and `_make_sell_receipt`
computes `net = gross - fees - taxes` (cash in after costs), then lays out the
cash / securities / fees / taxes entries so debits equal credits. If you add a
cost component (a new tax, an FX charge), add it as its own `Entry` on **both**
sides' builders and keep `balanced()` true - the `test_ledger.py` balance tests
will catch a one-sided change. Compare money with a tolerance (`abs(a - b) <
1e-9`), as `balanced()` and the tests do; never `==` on floats.

## Mock vs live: same contract, different home and type rigour

- `MockBroker` (`examples/brokers/mockbroker.py`) is the backtest broker:
  fixed starting capital (500.0), zero fees, deterministic `price()`. It is what
  the tests and `scripts/fuzz-strat.py` run against.
- `Trading212Broker` (`examples/brokers/trading212.py`) is a real-money adapter
  over the Trading 212 REST API. Its `buy()` / `sell()` are still TODO stubs;
  the read methods (capital, position, price) are wired.

Both live under `examples/`, which is **outside the mypy gate** (CI runs `mypy
broker trader` only, and `pyproject.toml` excludes `examples` from bandit too).
That is deliberate: the typed contract is the `Broker` ABC in `broker/`; the
adapters are reference implementations. The raw `Trading212` client class is
intentionally untyped and is not itself a `Broker` - only `Trading212Broker`
(which multiply-inherits `Trading212, Broker`) satisfies the contract. Do not
"fix" the untyped client by dragging it under the mypy gate without moving it
into `broker/` and committing to maintaining the types.

## Live-execution safety

`Trading212Broker.buy()` / `sell()` move real money once implemented. Anything
that places an order belongs behind an explicit live-vs-paper mode check
(`Trading212` already carries a `mode` of `live` / `demo` in its API host).
When implementing the order stubs, default to the safe path and require an
explicit opt-in for live orders - do not let a backtest accidentally route to a
real account.

## Anti-patterns to catch

- Treating `fees()` / `stamp_duty()` as absolute amounts instead of rates.
- Swapping the `buy`/`sell` argument meanings (cash vs units) - they are
  asymmetric on purpose.
- Building a `Receipt` by hand or appending to `self.ledger` directly instead of
  calling `_record_buy` / `_record_sell`.
- Adding a cost to one receipt builder but not the other, breaking `balanced()`.
- `==` on float money instead of a `1e-9` tolerance.
- Adding an abstract method to `Broker` without implementing it in both
  `MockBroker` and `Trading212Broker`.
- Routing a live order without a mode guard.

## Canonical examples

- `broker/broker.py` - the ABC and the `_record_*` helpers.
- `broker/ledger.py` - the frozen `Receipt` / `Entry` model and the balanced
  builders.
- `examples/brokers/mockbroker.py` - the minimal full implementation.
- `tests/test_ledger.py` - the balance and net-computation assertions your
  change must keep green.

## Upstream alignment

Double-entry bookkeeping is the standard accounting model (every debit has an
equal credit); this skill carries only how traderbot applies it (frozen
receipts, the rate-vs-absolute fee convention, the mock/live split). For the
Trading 212 API surface the live adapter targets, see
`proposals/trading212-swagger.md`.
