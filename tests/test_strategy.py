import pandas as pd
import pytest

from trader.indicators import Indicator, Signal
from trader.strategy import DefaultStrategy


class _Fixed(Indicator):
    """Stub indicator that always returns the same signal."""

    def __init__(self, sig: Signal) -> None:
        self._sig = sig

    def signal(self, df: pd.DataFrame) -> Signal:
        return self._sig


_DF = pd.DataFrame({"Close": [1.0]})


@pytest.mark.unit
class TestDefaultStrategy:
    def test_hold_with_no_indicators(self) -> None:
        assert DefaultStrategy().signal(_DF) == Signal.HOLD

    def test_buy_majority(self) -> None:
        strat = DefaultStrategy()
        strat.add_indicator(_Fixed(Signal.BUY))
        strat.add_indicator(_Fixed(Signal.BUY))
        strat.add_indicator(_Fixed(Signal.SELL))
        assert strat.signal(_DF) == Signal.BUY

    def test_sell_majority(self) -> None:
        strat = DefaultStrategy()
        strat.add_indicator(_Fixed(Signal.SELL))
        strat.add_indicator(_Fixed(Signal.SELL))
        strat.add_indicator(_Fixed(Signal.BUY))
        assert strat.signal(_DF) == Signal.SELL

    def test_hold_on_tie(self) -> None:
        strat = DefaultStrategy()
        strat.add_indicator(_Fixed(Signal.BUY))
        strat.add_indicator(_Fixed(Signal.SELL))
        assert strat.signal(_DF) == Signal.HOLD

    def test_hold_when_all_hold(self) -> None:
        strat = DefaultStrategy()
        strat.add_indicator(_Fixed(Signal.HOLD))
        strat.add_indicator(_Fixed(Signal.HOLD))
        assert strat.signal(_DF) == Signal.HOLD

    def test_add_indicator_appends(self) -> None:
        strat = DefaultStrategy()
        ind = _Fixed(Signal.BUY)
        strat.add_indicator(ind)
        assert ind in strat.indicators
