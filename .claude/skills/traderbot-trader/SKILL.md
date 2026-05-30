---
name: traderbot-trader
description: The Trader engine - position sizing (10% max bet), the fee/tax-netted minimum-profit sell gate, the TraderState machine, and the buy/sell guards. Load before editing trader/trader.py or trader/state.py.
---

# The Trader engine

`trader/trader.py` is the loop that turns a `Strategy`'s `Signal` into actual
broker calls. It owns the money-management rules the strategy layer does not:
how much to stake, when a sell is worth taking, and the lifecycle state. It
reads the decision from `strategy.signal(...)` and the prices/fees from the
`Broker`; it does not compute indicators itself.

## Construction wires capital, sizing, and the strategy

```python
self.position = self.broker.position(self.stock.symbol)
self.capital = self.broker.capital()
self.initial_capital = self.capital
self.trade_max_bet = self.initial_capital * 0.1     # stake cap: 10% of starting capital
self.trade_min_profit = self.trade_max_bet * 0.1    # sell only if net profit clears this
self.strategy.configure(self.broker, self.stock.symbol)  # hand the strategy fee context
```

`configure()` must be called here so fee-aware strategies (see
`traderbot-strategy`) get their broker context before the first decision. The
two sizing constants are the engine's risk policy:

- `trade_max_bet` caps any single buy at 10% of the *initial* capital (not the
  current balance) - the bot never goes all-in on one signal.
- `trade_min_profit` is the floor a sell must clear after costs.

If you change either constant or its base, that is a risk-policy change - call it
out explicitly and update `test_trader.py` (which pins `trade_max_bet == 50.0`
and `trade_min_profit == 5.0` for 500.0 starting capital).

## The buy/sell guards and the sell profit gate

```python
def buy(self) -> None:
    if self.capital <= 0.0:
        raise ValueError("cannot buy: no capital available")
    tender = self.capital if self.trade_max_bet > self.capital else self.trade_max_bet
    self.position += self.broker.buy(self.stock.symbol, tender)
    self.capital -= tender

def sell(self) -> None:
    if self.position <= 0.0:
        raise ValueError("cannot sell: no position held")
    gross = self.position * self.broker.price(self.stock.symbol)
    tax = self.broker.stamp_duty(self.stock.symbol)
    fees = self.broker.fees(self.stock.symbol)
    net = gross - ((gross * tax) + (gross * fees))
    if net > self.trade_min_profit:        # the profit gate
        self.capital += self.broker.sell(self.stock.symbol, self.position)
        self.position = 0
```

Two rules are load-bearing:

- **Buy caps at `trade_max_bet`** but spends everything if the balance is below
  the cap (`tender = capital if max_bet > capital else max_bet`). Keep that
  branch - the tests pin both the capped and the spend-it-all cases.
- **Sell only fires when `net > trade_min_profit`**, where `net` subtracts both
  the fee rate and the stamp-duty rate applied to the gross. This is the
  engine's backstop against churning a position out for less than it costs to
  exit - the partner to the strategy-side fee awareness. Do not drop the gate or
  compute `net` without both cost components.

The guards raise `ValueError` with messages the tests match on (`"no capital"`,
`"no position"`). Preserve the message substrings if you touch them.

## The TraderState machine

`trader/state.py` defines `TraderState` (`WAITING`, `BUYING`, `HOLDING`,
`SELLING`). `buy()` walks `BUYING -> HOLDING`; `sell()` walks `SELLING ->
WAITING`. The states are an integer enum used for lifecycle tracking. Keep the
transitions consistent if you add a state - a half-set state confuses any
consumer reading `self.state`.

## trade() dispatches on the Signal

```python
match self.evaluate():
    case Signal.BUY:  ... if self.capital > 0.0: self.buy()
    case Signal.SELL: ... if self.position > 0.0: self.sell()
    case Signal.HOLD: pass
```

`evaluate()` appends the latest bar (`stock.tail()`) to the analysis frame and
asks the strategy. Note `match` is a `match`/`case` statement (requires Python
3.10, which `pyproject.toml` pins as the floor) - keep all three `Signal` arms
covered.

## Anti-patterns to catch

- Changing `trade_max_bet` to a fraction of *current* capital instead of
  *initial* - that is a different (compounding) risk policy; the constant is
  pinned in tests.
- Removing or loosening the `net > trade_min_profit` sell gate, or computing
  `net` without both the fee and the stamp-duty component.
- Dropping the `capital <= 0` / `position <= 0` guards, or changing the
  `ValueError` message substrings the tests match.
- Computing position sizing inside a `Strategy` and again here - sizing today
  lives in the `Trader`; `proposals/position-sizing.md` is where moving it to
  the strategy is being designed, so coordinate rather than splitting it ad hoc.
- Leaving `self.state` in an intermediate (`BUYING` / `SELLING`) value after the
  method returns.

## Canonical examples

- `trader/trader.py` - the engine itself.
- `tests/test_trader.py` - pins the sizing constants, the capped/spend-all buy
  branches, the no-capital / no-position guards, and the trade() dispatch.

## Upstream alignment

The sizing and sell-gate rules are traderbot's own risk policy, not a framework
convention, so there is no upstream to defer to - but `proposals/position-
sizing.md` is the live design thread for making sizing pluggable. Read it before
reworking how much capital a signal deploys.
