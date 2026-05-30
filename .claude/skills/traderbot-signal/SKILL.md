---
name: traderbot-signal
description: The signal(df) -> Signal contract shared by every Indicator and Strategy. Decide only from the latest bar (no lookahead), return HOLD on insufficient data, never raise, no I/O. Load before editing any indicator under trader/indicators/ or any strategy in trader/strategy.py / trader/strategies/.
---

# The signal(df) -> Signal contract

Every `Indicator` and every `Strategy` in traderbot exposes the same method:

```python
def signal(self, df: pd.DataFrame) -> Signal:
    ...
```

`df` is OHLCV price history, oldest row first, newest row last. The method
returns one `Signal`: `BUY`, `SELL`, or `HOLD`. This skill is the universal
contract; `traderbot-indicator` and `traderbot-strategy` are specialisations
that stack on top of it. If you are editing an indicator or a strategy, both
this skill and the specialist load together - read both.

## No lookahead: decide from the last bar, never a future one

This is the load-bearing rule of the whole codebase. When `signal()` is called
live, the newest bar is `df.iloc[-1]` and **no bar after it exists yet**. The
decision must come from the tail of the frame:

```python
# correct - reads the most recent value(s)
if df["MACD"].iloc[-1] > df["MACD_S"].iloc[-1]:
    return Signal.BUY

# correct - a crossover reads the last two bars
prev_fast, curr_fast = df[fast_col].iloc[-2], df[fast_col].iloc[-1]
```

A backtest replays history bar by bar, so any value you read from a row *after*
the bar under decision is information the live trader could not have had. That
is lookahead bias, and it silently inflates backtest returns while the live bot
underperforms. Concretely, never:

- index a fixed forward offset (`df["Close"].iloc[i + 1]`, `.shift(-1)`),
- compute a statistic over the whole frame and compare the *current* bar to a
  future-inclusive aggregate (a rolling window ending at `-1` is fine; a
  centred window or a full-series `max()` used as a threshold for an interior
  bar is not),
- peek at `df.tail(n)` and then act on a bar that is not the last of that slice.

`rolling(window=w)` and `ewm(span=w)` are backward-looking by construction (each
output uses only that row and the ones before it), so they are safe. The danger
is in how you *index the result*, not in the moving average itself.

## HOLD on insufficient data - never raise

A rolling/ewm window over a short history yields `NaN` for the early rows, and
a freshly started trader may call `signal()` before there are enough bars. The
contract is to return `Signal.HOLD`, not to raise and not to guess:

```python
if len(df) < self._window:
    return Signal.HOLD

if math.isnan(df["RSI%"].iloc[-1]):
    return Signal.HOLD
```

`HOLD` means "no opinion this bar" and is always a safe answer. An exception out
of `signal()` aborts the trade loop; a wrong BUY/SELL on a NaN-driven comparison
spends real capital. Guard the insufficient-data and NaN cases explicitly. See
`SMACrossover` / `EMACrossover` (the `len(df) < 2` guard) and
`ResidualStrengthIndex` (the `math.isnan` guard) for the canonical shape.

## Signal is an integer enum so votes can be summed

`Signal` (in `trader/indicators/signal.py`) is `SELL = -1`, `HOLD = 0`,
`BUY = 1`. The integer values are deliberate: `DefaultStrategy` aggregates its
indicators by counting BUY and SELL votes. Do not reorder the values, add new
members, or convert to strings for logic. `Signal` is produced programmatically
only - there is intentionally no `from_str()` (round-trip via `Signal(int(v))`
if you ever need to persist one).

## No side effects beyond the documented DataFrame columns, no I/O

`signal()` is called inside the hot trade loop, potentially every bar. It must
not download data, read or write files, sleep, or hit the network - the data
layer (`Stock`) owns all I/O and hands `signal()` a ready frame. Indicators do
currently mutate `df` in place to add their computed columns (see
`traderbot-indicator` for that convention and the isolation proposal); that is
the only side effect the contract allows.

## Anti-patterns to catch

- `.iloc[i + 1]`, `.shift(-1)`, or any forward index inside `signal()` - lookahead.
- Comparing an interior bar against a full-series `df["Close"].max()` / `.min()`
  or a centred window - future-inclusive aggregate. Use a trailing
  `rolling(...).iloc[-1]` instead.
- Raising on short history instead of returning `HOLD`.
- A NaN comparison silently flowing to BUY/SELL because the insufficient-data
  guard is missing.
- String-comparing or arithmetic-free reinterpretation of `Signal` that breaks
  the `-1 / 0 / 1` vote-summing contract.
- File or network access inside `signal()`.

## Upstream alignment

The trailing-window / no-lookahead discipline is the backtesting analogue of
the "validate at the boundary" stance: it is enforced by convention here, not by
a framework. For the general bias taxonomy (lookahead, survivorship, data
snooping) see Investopedia's
[lookahead bias](https://www.investopedia.com/terms/l/lookaheadbias.asp). This
skill is the traderbot-specific overlay: the exact contract (`HOLD` on
insufficient data, integer `Signal` for voting, no I/O) and where each rule is
already practised in the codebase.
