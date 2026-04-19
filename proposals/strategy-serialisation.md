# Proposal: Strategy Serialisation (load / save)

## Problem

`fuzz-strat.py` wants to persist the best-performing strategy and reload it as a baseline for the next fuzzing run. `Strategy.load()` and `Strategy.save()` are stubs. There's currently no way to round-trip a strategy (its indicator types + parameter values) to disk.

## Proposed Format

JSON — human-readable, no dependencies, easy to inspect and edit by hand.

```json
{
  "strategy": "DefaultStrategy",
  "indicators": [
    {"type": "SimpleMovingAverage", "window": 5},
    {"type": "SimpleMovingAverage", "window": 20},
    {"type": "BollingerBands", "window": 20, "num_std": 2.0},
    {"type": "MACD", "k_period": 12, "d_period": 26, "t_period": 9},
    {"type": "ResidualStrengthIndex", "window": 14, "overbought": 70, "oversold": 30},
    {"type": "StochasticOscillation", "k_period": 14, "d_period": 3, "overbought": 80, "oversold": 20}
  ]
}
```

## Proposed Implementation

Each `Indicator` subclass implements two small methods:

```python
class Indicator(ABC):
    def to_dict(self) -> dict:
        """Return constructor params as a plain dict."""
        ...

    @classmethod
    def from_dict(cls, params: dict) -> "Indicator":
        """Reconstruct from the dict returned by to_dict()."""
        return cls(**params)
```

A registry maps type names to classes. `Strategy.save()` / `Strategy.load()` use it:

```python
INDICATOR_REGISTRY: dict[str, type[Indicator]] = {
    "SimpleMovingAverage": SimpleMovingAverage,
    "BollingerBands": BollingerBands,
    ...
}

class Strategy:
    def save(self, path: str) -> None:
        ...

    @classmethod
    def load(cls, path: str) -> "Strategy":
        ...
```

## Files Affected

- `trader/indicators/indicator.py` — add `to_dict()` / `from_dict()` to ABC
- Each indicator in `trader/indicators/` — implement `to_dict()`
- `trader/strategy.py` — implement `save()` / `load()` + registry
- `scripts/fuzz-strat.py` — wire up the load/save calls
- `tests/test_serialisation.py` — round-trip tests for each indicator type
