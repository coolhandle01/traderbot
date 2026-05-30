---
name: traderbot-strategy
description: How to write a Strategy in traderbot - subclass Strategy, implement signal(df) -> Signal, use configure(broker, symbol) to receive fee context, and never signal a trade that cannot clear round-trip costs. Builds on traderbot-signal. Load before editing trader/strategy.py or any file under trader/strategies/.
---

# Writing a Strategy

Builds on `traderbot-signal` (the universal `signal(df) -> Signal` contract).
A `Strategy` is what the `Trader` asks for a decision each bar. It either
aggregates several indicators (`DefaultStrategy`) or implements standalone logic
(`BuyAndHold`, `DollarCostAverage`, `Swing`). Both this skill and the signal
contract load on a strategy edit; read the signal contract first.

## The Strategy ABC

`trader/strategy.py`:

```python
class Strategy(ABC):
    def configure(self, broker: Broker, symbol: str) -> None:  # noqa: B027
        """Called by Trader after construction; override to receive fee context."""

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        ...
```

`configure()` is a deliberately-empty base hook - the `# noqa: B027` says so:
an abstract empty method would force every subclass to implement it, but most
strategies do not need fee context, so the base is a concrete no-op and only
fee-aware subclasses override it. Keep the `noqa` and its reason if you touch
the base.

`DefaultStrategy` lives in the same file and is the indicator-aggregating
strategy:

```python
class DefaultStrategy(Strategy):
    def __init__(self) -> None:
        self.indicators: list[Indicator] = []

    def add_indicator(self, indicator: Indicator) -> None:
        self.indicators.append(indicator)

    def signal(self, df: pd.DataFrame) -> Signal:
        signals = [ind.signal(df) for ind in self.indicators]
        buys = sum(1 for s in signals if s == Signal.BUY)
        sells = sum(1 for s in signals if s == Signal.SELL)
        total = len(signals)
        if total == 0:
            return Signal.HOLD
        if buys > total / 2:
            return Signal.BUY
        if sells > total / 2:
            return Signal.SELL
        return Signal.HOLD
```

Majority vote with HOLD on ties and on an empty indicator list. The vote relies
on `Signal` being summable - see `traderbot-signal`. Standalone strategies
(`trader/strategies/`) subclass `Strategy` directly and carry their own state
(`BuyAndHold._bought`, `DollarCostAverage._bar`).

## Fee-aware: never signal a trade that cannot clear round-trip costs

This is the strategy-layer safety rule. A round trip pays the broker's fee on
both legs plus stamp duty; a signal that triggers a trade smaller than that cost
loses money before the price even moves. Fee-aware strategies pull the rates in
`configure()` and lift their own threshold above breakeven:

```python
def configure(self, broker: Broker, symbol: str) -> None:
    round_trip = broker.fees(symbol) * 2 + broker.stamp_duty(symbol)
    self._threshold = max(self._threshold, round_trip + 0.005)  # buffer above breakeven
```

`Swing` does exactly this; `DollarCostAverage.configure()` computes a minimum
trade size from the same rates. When you add a strategy whose edge is a small
price move, gate it on the round-trip cost in `configure()`. The `Trader` also
enforces a profit floor on the sell side (`trade_min_profit`, see
`traderbot-trader`), but that is the engine's backstop, not a substitute for the
strategy refusing an unprofitable entry.

`configure()` receives the broker, not a cached fee number - rates can differ
per symbol and per broker (a live broker may charge what `MockBroker` reports as
zero). Read them through the broker every time `configure()` runs.

## State across bars is fine, but it must be deterministic

Strategies may hold state between `signal()` calls (`_bought`, `_bar`
counters). That is allowed and is how `BuyAndHold` and `DollarCostAverage` work.
Keep it deterministic: the same sequence of bars must produce the same signals,
so `scripts/fuzz-strat.py` and the backtest are reproducible. No clocks, no
randomness inside `signal()` (the fuzzer injects randomness at construction
time, not per bar).

## Anti-patterns to catch

- A new edge-seeking strategy that signals BUY/SELL without checking the
  round-trip cost in `configure()` - it will churn capital into fees.
- Caching a fee number at construction instead of reading it from the broker in
  `configure()` - misses per-symbol and live-vs-mock differences.
- Removing the `# noqa: B027` (or its reason) from the base `configure()` -
  that turns the intentional concrete no-op back into a churn warning.
- Randomness or wall-clock reads inside `signal()` - breaks reproducibility.
- Reimplementing majority-vote aggregation when `DefaultStrategy` already does
  it; add indicators to a `DefaultStrategy` instead.

## Canonical examples

- `trader/strategy.py` - the ABC and `DefaultStrategy` majority vote.
- `trader/strategies/swing.py` - the fee-aware `configure()` threshold bump.
- `trader/strategies/dca.py` - `configure()` deriving a minimum trade size.
- `trader/strategies/buyandhold.py` - the passive benchmark every active
  strategy must beat; the minimal stateful strategy.

## Upstream alignment

Position-sizing is an active design area - `proposals/position-sizing.md`
proposes a `stake()` method on `Strategy` so a strategy can size each trade, not
just signal direction. If your change touches how much capital a signal deploys,
read that proposal first rather than wiring sizing ad hoc into the `Trader`.
