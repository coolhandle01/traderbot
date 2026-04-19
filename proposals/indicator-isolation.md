# Proposal: Indicator Isolation (column namespacing + concurrency safety)

## Problems

### 1. Column name clashes

Every indicator mutates the same shared DataFrame in-place.  Several use generic
column names that silently overwrite each other when the same indicator is used
twice with different parameters, or when a future indicator happens to use the
same name:

| Indicator | Generic columns |
|-----------|----------------|
| RSI | `gain`, `loss`, `avg_gain`, `avg_loss`, `RS`, `RSI%` |
| SO  | `n_high`, `n_low`, `%K`, `%D` |

Running `RSI(14)` and `RSI(28)` in the same strategy: the second silently
overwrites the first's intermediate columns.  Same for two `SO` instances.

### 2. Concurrency is unsafe

The intended architecture has a price-polling thread (`stock.update()`) writing
new rows to the history DataFrame while a trading thread reads the same object
and writes indicator columns to it.  pandas DataFrames are not thread-safe —
concurrent reads and writes produce torn data, interleaved column writes, or
internal numpy array corruption.

## Proposed Fix

### Part A — Indicators stop mutating the input DataFrame

Each indicator works on a **local copy** and returns only the Signal.
Intermediate series (needed by the chart) are stored as instance attributes
after each `signal()` call, not written back to the shared DataFrame.

```python
class ResidualStrengthIndex(Indicator):
    def signal(self, df: pd.DataFrame) -> Signal:
        diff = df["Close"].diff()
        gain = diff.clip(lower=0).round(2)
        loss = diff.clip(upper=0).abs().round(2)

        # Wilder smoothing — all local, nothing written to df
        avg_gain = gain.rolling(window=self.window, min_periods=self.window).mean().copy()
        avg_loss = loss.rolling(window=self.window, min_periods=self.window).mean().copy()
        for i in range(len(df) - self.window - 1):
            j, k = i + self.window, i + self.window + 1
            avg_gain.iloc[k] = (avg_gain.iloc[j] * (self.window - 1) + gain.iloc[k]) / self.window
            avg_loss.iloc[k] = (avg_loss.iloc[j] * (self.window - 1) + loss.iloc[k]) / self.window

        rs = avg_gain / avg_loss
        self.rsi = 100 - (100 / (1.0 + rs))   # exposed for charting

        last = self.rsi.iloc[-1]
        if math.isnan(last):
            return Signal.HOLD
        if last > self.overbought:
            return Signal.SELL
        if last < self.oversold:
            return Signal.BUY
        return Signal.HOLD
```

`Report` then reads `indicator.rsi`, `indicator.macd`, etc. directly instead
of pulling named columns from the DataFrame.  The price DataFrame stays clean —
only OHLCV columns, never modified by indicators.

### Part B — Concurrency via snapshot + queue

Replace the shared-mutable-DataFrame pattern with a producer/consumer queue:

```
┌─────────────────┐        queue.Queue        ┌──────────────────────┐
│  Polling thread │ ──── pd.DataFrame copy ──▶│  Trading thread      │
│  (yfinance)     │                            │  strategy.signal()   │
│  stock.update() │                            │  broker.buy/sell()   │
└─────────────────┘                            └──────────────────────┘
```

```python
import queue, threading

bar_queue: queue.Queue[pd.DataFrame] = queue.Queue(maxsize=1)

def poll(stock: Stock) -> None:
    while True:
        stock.update()
        # put() a deep copy — polling thread keeps no reference after this
        bar_queue.put(stock.copy())
        time.sleep(60)

def trade(trader: Trader) -> None:
    while True:
        snapshot = bar_queue.get()   # blocks until a new bar arrives
        trader.trade(snapshot)       # operates on the snapshot, never shared state

threading.Thread(target=poll, args=(stock,), daemon=True).start()
trade(trader)
```

`Trader.trade()` receives the snapshot and passes it to indicators — all reads
and writes stay within that thread.  No locks needed because the DataFrame is
never shared.

## Files Affected

- `trader/indicators/*.py` — remove all `df[col] = ...` writes; store results as instance attributes
- `trader/report.py` — read chart data from indicator attributes rather than DataFrame columns
- `trader/trader.py` — `trade()` accepts an optional snapshot DataFrame
- `example.py` — wire up the two-thread pattern
- `tests/` — update indicator tests (no longer need to check for columns on df)

## What This Gives You

- Two RSIs, two SOs, any combination → no silent overwrites
- Price history DataFrame is read-only after loading — safe to hand to any thread
- Clear ownership: polling thread owns the live DataFrame; trading thread owns snapshots
- Easier to test indicators in isolation (no DataFrame side-effects to set up)
