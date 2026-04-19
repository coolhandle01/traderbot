import pandas as pd
import pytest

from broker import Stock
from examples.brokers.mockbroker import MockBroker
from trader.indicators import Indicator, Signal
from trader.strategy import DefaultStrategy
from trader.trader import Trader


def _make_stock(closes: list[float]) -> Stock:
    """Build a Stock with fake history — no file I/O."""
    stock = object.__new__(Stock)
    stock.symbol = "TEST"
    stock.interval = "1d"
    stock.archive = ""
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="D")
    stock.history = pd.DataFrame(
        {"Close": closes, "Open": closes, "High": closes, "Low": closes},
        index=idx,
    )
    return stock


class _Fixed(Indicator):
    def __init__(self, sig: Signal) -> None:
        self._sig = sig

    def signal(self, df: pd.DataFrame) -> Signal:
        return self._sig


def _trader(signal: Signal, capital: float = 500.0) -> Trader:
    stock = _make_stock([float(i + 1) for i in range(30)])
    broker = MockBroker()
    broker.current_capital = capital
    strat = DefaultStrategy()
    strat.add_indicator(_Fixed(signal))
    return Trader(stock, broker, strat)


@pytest.mark.unit
class TestTraderInit:
    def test_capital_from_broker(self) -> None:
        t = _trader(Signal.HOLD)
        assert t.capital == 500.0

    def test_initial_position_zero(self) -> None:
        t = _trader(Signal.HOLD)
        assert t.position == 0.0

    def test_trade_max_bet_is_10_percent(self) -> None:
        t = _trader(Signal.HOLD)
        assert t.trade_max_bet == 50.0

    def test_trade_min_profit_is_10_percent_of_max_bet(self) -> None:
        t = _trader(Signal.HOLD)
        assert t.trade_min_profit == 5.0


@pytest.mark.unit
class TestTraderBuy:
    def test_buy_caps_at_max_bet(self) -> None:
        t = _trader(Signal.HOLD)
        t.buy()
        assert t.capital == 450.0  # 500 - 50 (max bet)

    def test_buy_increases_position(self) -> None:
        t = _trader(Signal.HOLD)
        t.buy()
        assert t.position > 0.0

    def test_buy_uses_all_capital_when_below_max_bet(self) -> None:
        t = _trader(Signal.HOLD)  # max_bet = 50.0
        t.capital = 10.0  # less than max_bet → spend it all
        t.buy()
        assert t.capital == 0.0

    def test_buy_raises_with_no_capital(self) -> None:
        t = _trader(Signal.HOLD, capital=0.0)
        with pytest.raises(ValueError, match="no capital"):
            t.buy()


@pytest.mark.unit
class TestTraderSell:
    def test_sell_raises_with_no_position(self) -> None:
        t = _trader(Signal.HOLD)
        with pytest.raises(ValueError, match="no position"):
            t.sell()

    def test_sell_clears_position_when_profitable(self) -> None:
        t = _trader(Signal.HOLD)
        t.buy()
        t.sell()
        assert t.position == 0

    def test_sell_returns_capital(self) -> None:
        t = _trader(Signal.HOLD)
        t.buy()
        capital_before = t.capital
        t.sell()
        assert t.capital > capital_before


@pytest.mark.unit
class TestTraderTrade:
    def test_trade_buys_on_buy_signal(self) -> None:
        t = _trader(Signal.BUY)
        t.trade()
        assert t.position > 0.0

    def test_trade_sells_on_sell_signal_when_holding(self) -> None:
        t = _trader(Signal.BUY)
        t.trade()
        # now flip to SELL
        t.strategy.indicators[0] = _Fixed(Signal.SELL)
        t.trade()
        assert t.position == 0

    def test_trade_hold_changes_nothing(self) -> None:
        t = _trader(Signal.HOLD)
        t.trade()
        assert t.position == 0.0
        assert t.capital == 500.0
