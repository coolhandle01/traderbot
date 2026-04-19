# Proposal: Position Sizing in Strategy

## Problem

`Trader.buy()` always stakes 100% of available capital and `Trader.sell()` always exits the full position. There's no way to express rules like "don't stake more than 10% of capital" or "once in profit, only risk the profit".

## Proposed Change

Add an optional `stake()` method to `Strategy` with a default that preserves the current all-in behaviour:

```python
class Strategy(ABC):
    def stake(self, capital: float, position_value: float) -> float:
        """
        Return the amount of capital to deploy on the next BUY signal.

        capital        — uninvested cash available
        position_value — current market value of the open position

        Default: stake everything (current behaviour).
        Override to enforce sizing rules.
        """
        return capital
```

`Trader.buy()` calls `self.strategy.stake(self.capital, position_value)` instead of using `self.capital` directly.

## Example Overrides

```python
class CappedStrategy(DefaultStrategy):
    """Never stake more than `max_pct` of total portfolio value."""
    def __init__(self, max_pct: float = 0.10):
        super().__init__()
        self.max_pct = max_pct

    def stake(self, capital: float, position_value: float) -> float:
        portfolio = capital + position_value
        return min(capital, portfolio * self.max_pct)


class ProfitOnlyStrategy(DefaultStrategy):
    """Once in a position, only reinvest gains above the initial stake."""
    def __init__(self, initial_stake: float):
        super().__init__()
        self.initial_stake = initial_stake

    def stake(self, capital: float, position_value: float) -> float:
        profit = max(0.0, capital - self.initial_stake)
        return profit
```

## Files Affected

- `trader/strategy.py` — add `stake()` with default
- `trader/trader.py` — call `strategy.stake()` in `buy()`
- `tests/test_strategy.py` — unit tests for both overrides
