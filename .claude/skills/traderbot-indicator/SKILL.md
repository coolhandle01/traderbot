---
name: traderbot-indicator
description: How to write a technical Indicator in traderbot - subclass Indicator, implement signal(df) -> Signal, take window/period params in __init__, compute with pandas, decide from the last bar. Builds on traderbot-signal. Load before editing any file under trader/indicators/.
---

# Writing an Indicator

Builds on `traderbot-signal` (the universal `signal(df) -> Signal` contract -
no lookahead, HOLD on insufficient data, integer Signal). This skill adds the
indicator-specific mechanics. Both load together on a `trader/indicators/*.py`
edit; read the signal contract first.

## The Indicator ABC

`trader/indicators/indicator.py` defines:

```python
class Indicator(ABC):
    def __init__(self) -> None:
        self.analysis = pd.DataFrame()

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> Signal:
        pass
```

A new indicator subclasses it and implements `signal()`. Construction takes the
tuning parameters (windows, periods, thresholds) and stores them on `self`; it
does **not** take price data. Price arrives later, per call, as the `df`
argument.

```python
class BollingerBands(Indicator):
    def __init__(self, window: int, num_std: float) -> None:
        self.window = window
        self.num_std = num_std

    def signal(self, df: pd.DataFrame) -> Signal:
        sma = df["Close"].rolling(window=self.window).mean()
        std = df["Close"].rolling(window=self.window).std()
        df["BB_H"] = sma + (std * self.num_std)
        df["BB_L"] = sma - (std * self.num_std)
        last_close = df["Close"].iloc[-1]
        if last_close > df["BB_H"].iloc[-1]:
            return Signal.SELL
        if last_close < df["BB_L"].iloc[-1]:
            return Signal.BUY
        return Signal.HOLD
```

Constructor params are plain typed scalars (`int` windows, `float` thresholds).
Keep the names a quant would recognise (`window`, `k_period`, `d_period`,
`overbought`, `oversold`, `fast`, `slow`) and document the values it was tuned
with in the docstring, as the existing indicators do.

## Compute on `df["Close"]` (and High/Low) with pandas

The frame carries `Open`, `High`, `Low`, `Close` columns. Most indicators read
`df["Close"]`; range indicators (`StochasticOscillation`) also read `High` /
`Low`. Use vectorised pandas - `.rolling()`, `.ewm()`, `.diff()`, `.clip()` -
not Python loops, except where the algorithm is genuinely recursive (RSI's
Wilder smoothing is the one looped example, and it is commented as such).

Pass `min_periods=window` to `rolling` / `ewm` when an early partial window
would otherwise produce a misleadingly confident value - MACD does this so the
EMA does not emit a number before it has seen a full span.

## The in-place DataFrame convention (and its known limit)

Indicators currently write their intermediate series back onto the shared `df`
as new columns (`df["MACD"]`, `df["SO_K%"]`, `df["BB_H"]`, ...). `Report` then
reads those columns to chart them. Follow the existing convention when adding to
an existing indicator: namespace your columns with the indicator's tag so they
read clearly on the chart.

Be aware this convention has a documented flaw: two instances of the same
indicator with different parameters silently overwrite each other's columns, and
the shared mutable frame is not thread-safe. The fix - indicators compute on a
local copy and expose results as instance attributes instead of mutating `df` -
is specced in `proposals/indicator-isolation.md`. Do not start a partial
migration inside an unrelated change; if your edit is the isolation work, follow
the proposal and update `Report` and the indicator tests together. Until then,
pick column names that will not collide (the generic `gain` / `loss` /
`n_high` / `n_low` names called out in the proposal are the cautionary
examples).

## Column-name coupling with Report

`trader/report.py` reads specific column names back off the frame
(`SMA5`/`SMA10`/`SMA20`, `BB_H`/`BB_L`, `SO_K%`/`SO_D%`, `MACD`/`MACD_S`/
`MACD_H`). If you rename a column an indicator writes, you break the chart. If
you spot an existing mismatch (Report reads a name no indicator writes), it is a
FIXME, not something to silently "fix" by renaming in an unrelated PR - surface
it.

## Register the indicator in the package __init__

Add the class to `trader/indicators/__init__.py` (`__all__` plus the import) so
strategies can `from trader.indicators import YourIndicator`. The
`scripts/fuzz-strat.py` random-strategy builder and `Report` both rely on the
public surface.

## Anti-patterns to catch

- Taking price data in `__init__` instead of in `signal(df)`. The indicator is
  reusable across stocks; only parameters belong on the instance.
- A Python `for` loop over rows where a vectorised pandas op would do (the RSI
  Wilder loop is the documented exception, not a template to copy).
- Dropping `min_periods` and acting on a value computed from a partial window.
- A new generic column name (`high`, `low`, `signal`, `avg`) that can collide
  with another indicator's columns - namespace it.
- Renaming a column `Report` reads without updating `Report` in the same change.
- An indicator that only adds chart columns but returns a real BUY/SELL - if it
  is chart-only, return `HOLD` (see `SimpleMovingAverage`, which is explicitly
  a chart indicator and always holds).

## Canonical examples

- `trader/indicators/bb.py`, `macd.py` - trailing-window indicators that decide
  from `.iloc[-1]`.
- `trader/indicators/crossover.py` - the two-bar (`.iloc[-2]` vs `.iloc[-1]`)
  crossover shape with the `len(df) < 2` guard.
- `trader/indicators/rsi.py` - the one place a row loop is justified (Wilder
  smoothing), plus the `math.isnan` HOLD guard.
- `trader/indicators/ma.py` - the chart-only indicator that always returns HOLD.

## Upstream alignment

The maths behind each indicator is standard technical analysis - each file
already cites its reference (Investopedia, alpharithms, StockCharts) in the
module docstring. Keep that citation habit: a new indicator names the source it
implements. This skill carries only the traderbot conventions (the ABC shape,
the in-place-column convention and its proposal, the Report coupling), not the
indicator maths.
