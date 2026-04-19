import pandas as pd
import pytest

from trader.indicators import Signal
from trader.strategies import BuyAndHold, DollarCostAverage, Swing


def _df(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"Close": closes})


@pytest.mark.unit
class TestBuyAndHold:
    def test_first_signal_is_buy(self) -> None:
        assert BuyAndHold().signal(_df([100.0])) == Signal.BUY

    def test_second_signal_is_hold(self) -> None:
        strat = BuyAndHold()
        strat.signal(_df([100.0]))
        assert strat.signal(_df([101.0])) == Signal.HOLD

    def test_never_sells(self) -> None:
        strat = BuyAndHold()
        results = [strat.signal(_df([float(i)])) for i in range(1, 50)]
        assert Signal.SELL not in results


@pytest.mark.unit
class TestDollarCostAverage:
    def test_hold_before_first_interval(self) -> None:
        strat = DollarCostAverage(interval=5)
        for _ in range(4):
            assert strat.signal(_df([100.0])) == Signal.HOLD

    def test_buy_at_interval(self) -> None:
        strat = DollarCostAverage(interval=5)
        results = [strat.signal(_df([100.0])) for _ in range(5)]
        assert results[-1] == Signal.BUY

    def test_buy_at_each_multiple_of_interval(self) -> None:
        strat = DollarCostAverage(interval=3)
        results = [strat.signal(_df([100.0])) for _ in range(9)]
        buys = [i for i, s in enumerate(results, 1) if s == Signal.BUY]
        assert buys == [3, 6, 9]

    def test_never_sells(self) -> None:
        strat = DollarCostAverage(interval=1)
        results = [strat.signal(_df([100.0])) for _ in range(20)]
        assert Signal.SELL not in results


@pytest.mark.unit
class TestSwing:
    def _flat_then(self, end: float, window: int = 5) -> pd.DataFrame:
        closes = [100.0] * (window - 1) + [end]
        return _df(closes)

    def test_hold_on_insufficient_data(self) -> None:
        assert Swing(window=20).signal(_df([100.0])) == Signal.HOLD

    def test_buy_on_dip(self) -> None:
        # price spikes high then crashes — should trigger BUY
        closes = [100.0] * 4 + [200.0] + [10.0]
        assert Swing(window=6, threshold=0.05).signal(_df(closes)) == Signal.BUY

    def test_sell_on_bounce(self) -> None:
        # price crashes low then recovers sharply — should trigger SELL
        closes = [100.0] * 4 + [10.0] + [200.0]
        assert Swing(window=6, threshold=0.05).signal(_df(closes)) == Signal.SELL

    def test_hold_within_threshold(self) -> None:
        closes = [100.0] * 6
        assert Swing(window=6, threshold=0.05).signal(_df(closes)) == Signal.HOLD

    def test_configure_bumps_threshold_for_fees(self) -> None:
        from examples.brokers.mockbroker import MockBroker

        class FeebrokerStub(MockBroker):
            def fees(self, symbol: str) -> float:
                return 0.10  # 10% fee — absurdly high, threshold must exceed it

        strat = Swing(window=5, threshold=0.01)
        strat.configure(FeebrokerStub(), "AAPL")
        assert strat._threshold >= 0.205  # 0.10*2 + 0.005
