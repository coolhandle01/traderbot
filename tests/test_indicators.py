import pandas as pd
import pytest

from trader.indicators import MACD, Signal, SimpleMovingAverage
from trader.indicators.rsi import ResidualStrengthIndex


def _ohlcv(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"Close": closes, "High": closes, "Low": closes})


@pytest.mark.unit
class TestSignal:
    def test_buy_value(self) -> None:
        assert Signal.BUY.value == 1

    def test_sell_value(self) -> None:
        assert Signal.SELL.value == -1

    def test_hold_value(self) -> None:
        assert Signal.HOLD.value == 0


@pytest.mark.unit
class TestSimpleMovingAverage:
    def test_produces_signal(self) -> None:
        sma = SimpleMovingAverage(3)
        df = _ohlcv([10.0, 11.0, 12.0, 13.0, 14.0])
        assert sma.signal(df) in Signal

    def test_adds_column(self) -> None:
        sma = SimpleMovingAverage(3)
        df = _ohlcv([10.0, 11.0, 12.0])
        sma.signal(df)
        assert "SMA3" in df.columns


@pytest.mark.unit
class TestMACD:
    def test_buy_when_fast_above_slow(self) -> None:
        macd = MACD(3, 6, 2)
        closes = [float(i) for i in range(1, 20)]
        df = _ohlcv(closes)
        assert macd.signal(df) == Signal.BUY

    def test_sell_when_fast_below_slow(self) -> None:
        macd = MACD(3, 6, 2)
        closes = [float(20 - i) for i in range(20)]
        df = _ohlcv(closes)
        assert macd.signal(df) == Signal.SELL


@pytest.mark.unit
class TestRSI:
    def test_hold_on_insufficient_data(self) -> None:
        rsi = ResidualStrengthIndex(14, overbought=70.0, oversold=30.0)
        df = _ohlcv([100.0] * 5)
        assert rsi.signal(df) == Signal.HOLD
