---
name: traderbot-tests
description: How traderbot unit tests are written - synthetic OHLCV frames built by hand (no network), deterministic price series chosen to force a specific Signal, class-grouped tests under the unit marker, stub indicators, and Stock built without file I/O. Load before editing any file under tests/.
---

# Writing tests

traderbot tests are pure unit tests: no yfinance, no files, no real broker.
They build the price data by hand, run the thing under test, and assert the
`Signal` (or the money math). CI runs `pytest -m unit --cov`, so every test is
marked and must pass without network or disk.

## Mark every test `unit`

```python
@pytest.mark.unit
class TestBollingerBands:
    ...
```

The `unit` marker is declared in `pyproject.toml` and is what CI selects
(`pytest -m unit`). An unmarked test does not run in CI. Group related cases in
a `TestX` class named after the unit under test, one assertion-focused method
per behaviour (the existing files are the template).

## Build OHLCV frames by hand - never download

Indicator/strategy tests construct a small DataFrame directly. `test_indicators.py`
has the canonical helper:

```python
def _ohlcv(closes, highs=None, lows=None) -> pd.DataFrame:
    return pd.DataFrame({
        "Close": closes,
        "High": highs if highs is not None else closes,
        "Low":  lows  if lows  is not None else closes,
    })
```

Choose the price series to *force* the branch you are testing, and say why in a
comment:

```python
# Stable prices then a sharp spike -> close above upper band -> SELL
closes = [100.0] * 20 + [200.0]
assert bb.signal(_ohlcv(closes)) == Signal.SELL
```

Cover the three outcomes that matter for a signal producer: the BUY case, the
SELL case, the HOLD case, and the insufficient-data HOLD (`len(df) < window`).
Crossover and stochastic tests show how to engineer a series that crosses a
threshold on the last bar.

## Build a Stock without file I/O

When you need a `Stock` but not its yfinance/CSV machinery, bypass `__init__`
with `object.__new__` and set the fields directly (from `test_trader.py`):

```python
def _make_stock(closes: list[float]) -> Stock:
    stock = object.__new__(Stock)
    stock.symbol = "TEST"
    stock.interval = "1d"
    stock.archive = ""
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="D")
    stock.history = pd.DataFrame(
        {"Close": closes, "Open": closes, "High": closes, "Low": closes}, index=idx
    )
    return stock
```

This keeps the test offline and deterministic - no `load()`, no network.

## Stub indicators and strategies, drive the broker with MockBroker

To test the engine or aggregation in isolation, inject a fixed-signal stub
rather than a real indicator:

```python
class _Fixed(Indicator):
    def __init__(self, sig: Signal) -> None:
        self._sig = sig
    def signal(self, df: pd.DataFrame) -> Signal:
        return self._sig
```

This `_Fixed` stub appears in both `test_strategy.py` and `test_trader.py`. Use
`MockBroker` (zero fees, fixed 500.0 capital, price 1.0) as the broker under
test; set `broker.current_capital` directly to vary the capital case.

## Assert money math with a tolerance, not `==`

Ledger and fee tests compare floats with an epsilon, mirroring `Receipt.balanced()`:

```python
assert abs(r.fees - 1.0) < 1e-9
assert abs(r.net - (r.gross + r.fees + r.taxes)) < 1e-9
```

Never `==` on computed float money. Exact integer-ish values that are
constructed without arithmetic (`r.gross == 50.0`, `t.trade_max_bet == 50.0`)
may use `==`.

## Anti-patterns to catch

- A test that calls `Stock.load()`, `yf.download`, or reads a CSV - it will fail
  or flake in CI. Build the frame by hand.
- A test without `@pytest.mark.unit` - it silently does not run in CI.
- Asserting a single signal without also covering the HOLD / insufficient-data
  path for the same producer.
- `==` on computed float money instead of a `1e-9` tolerance.
- A price series that does not actually force the asserted branch (assert passes
  for the wrong reason) - comment why the series produces the expected signal.
- Reaching into a real broker or network when `MockBroker` and a hand-built
  `Stock` would isolate the unit.

## Canonical examples

- `tests/test_indicators.py` - the `_ohlcv` helper and the BUY/SELL/HOLD series.
- `tests/test_trader.py` - `_make_stock` (no-I/O Stock) and the `_Fixed` stub.
- `tests/test_ledger.py` - the tolerance-based money assertions.
- `tests/test_strategy.py` - aggregation tests driven by `_Fixed` stubs.

## Upstream alignment

Standard pytest - markers, class grouping, fixtures - is upstream
(<https://docs.pytest.org/>). This skill carries only the traderbot conventions:
the synthetic-OHLCV pattern, the no-I/O `Stock`, the `_Fixed` stub, the
force-the-branch discipline, and the float tolerance. Note `_Fixed` is currently
duplicated across two test files; if a shared test-fixtures module is
introduced, prefer importing it over copying the stub a third time.
