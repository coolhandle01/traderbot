---
name: traderbot-data
description: The Stock price-history layer - yfinance download, local CSV cache, and the deep-copy invariant on copy()/tail() that protects the cached history from in-place indicator mutation. Load before editing broker/stock.py.
---

# The data layer (Stock)

`broker/stock.py` owns all price-history I/O. `Stock` represents one ticker at
one interval, loads its OHLCV history from yfinance (cached to local CSV), and
hands clean frames to the trading logic. `StockAnalysis` and `PortfolioAnalysis`
compute performance metrics (returns, volatility, Sharpe, drawdown) off that
history. This is the only layer allowed to do I/O - indicators and strategies
receive ready frames (see `traderbot-signal`).

## The deep-copy invariant - do not weaken it

```python
def copy(self) -> pd.DataFrame:
    return self.history.copy(deep=True)  # type: ignore[no-any-return]

def tail(self) -> pd.DataFrame:
    return self.history.tail(1).copy(deep=True)  # type: ignore[no-any-return]
```

Both return a **deep** copy on purpose. Indicators mutate the frame they are
given in place (they add `MACD`, `BB_H`, ... columns - see
`traderbot-indicator`). If `copy()` / `tail()` handed out a view or a shallow
copy, those writes would corrupt the cached `self.history` and poison every
later read. The deep copy is what makes the cached history safe to hand to the
trading logic repeatedly. Do not "optimise" it to a shallow copy or a direct
return of `self.history`.

The `# type: ignore[no-any-return]` carries its reason in the rule code:
`DataFrame.copy()` is typed loosely upstream, so mypy cannot see the concrete
return type. Keep the targeted ignore (with its specific code), not a blanket
one, and keep it only on these returns.

## Point-in-time history

`history` is ordered oldest-first, newest-last, indexed by timestamp.
`update()` appends only genuinely new bars and de-duplicates against the
existing index:

```python
events = events.loc[~events.index.isin(self.history.index)]  # filter duplicates
```

Preserve that ordering and the de-dup. Downstream `signal()` code trusts that
`iloc[-1]` is the most recent bar and that there are no repeats; a re-ordering
or a duplicated tail row would quietly feed lookahead or double-counted bars
into every indicator.

## Caching and offline runs

`load()` reads the CSV at `history/<symbol>/<interval>.csv` and only calls
`download()` (the network) when the file is missing. This keeps backtests
reproducible and offline-friendly. Keep that read-cache-first behaviour: a unit
test or a backtest must be able to run against a cached CSV without hitting
yfinance. If you add a freshness check, make the offline path still work when
the network is unavailable.

## Analysis classes

`StockAnalysis` takes a `Stock` and computes daily returns, annualised return,
volatility, Sharpe, and max drawdown over a window (default 252 trading days).
It operates on the loaded `history` `Series` - keep its inputs as `Series`, not
single-column `DataFrame`s (a `float(DataFrame)` would raise; this was a
fixed CI bug). These metrics are read-only summaries; they must not mutate
`history`.

## Anti-patterns to catch

- Returning `self.history` or a shallow copy from `copy()` / `tail()` - lets
  indicator column-writes corrupt the cache.
- Widening the targeted `# type: ignore[no-any-return]` to a bare
  `# type: ignore`, or dropping its rationale.
- Re-ordering `history` newest-first, or losing the `update()` de-dup - feeds
  bad bars to every indicator.
- Making `load()` hit the network unconditionally - breaks offline/reproducible
  backtests.
- Computing analysis metrics off a single-column `DataFrame` instead of a
  `Series`.
- Doing price I/O anywhere other than this layer.

## Upstream alignment

The performance-metric formulas (annualised return, Sharpe, drawdown) follow the
standard portfolio-analysis definitions cited in the `Stock` module
(tradewithpython). yfinance owns the download contract. This skill carries only
the traderbot invariants: the deep-copy protection, point-in-time ordering, and
the cache-first offline path.
