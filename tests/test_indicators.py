import pandas as pd
import pytest

from trader.indicators import MACD, Signal, SimpleMovingAverage
from trader.indicators.bb import BollingerBands
from trader.indicators.rsi import ResidualStrengthIndex
from trader.indicators.so import StochasticOscillation


def _ohlcv(
    closes: list[float],
    highs: list[float] | None = None,
    lows: list[float] | None = None,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": closes,
            "High": highs if highs is not None else closes,
            "Low": lows if lows is not None else closes,
        }
    )


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
    def test_adds_column(self) -> None:
        sma = SimpleMovingAverage(3)
        df = _ohlcv([10.0, 11.0, 12.0])
        sma.signal(df)
        assert "SMA3" in df.columns

    def test_always_hold(self) -> None:
        # SMA is a chart indicator only — it never fires a signal by itself
        sma = SimpleMovingAverage(3)
        assert sma.signal(_ohlcv([10.0, 11.0, 12.0])) == Signal.HOLD


@pytest.mark.unit
class TestBollingerBands:
    def test_sell_when_price_above_upper_band(self) -> None:
        # Stable prices then a sharp spike → close above upper band → SELL
        closes = [100.0] * 20 + [200.0]
        bb = BollingerBands(window=20, num_std=2.0)
        assert bb.signal(_ohlcv(closes)) == Signal.SELL

    def test_buy_when_price_below_lower_band(self) -> None:
        # Stable prices then a sharp drop → close below lower band → BUY
        closes = [100.0] * 20 + [0.0]
        bb = BollingerBands(window=20, num_std=2.0)
        assert bb.signal(_ohlcv(closes)) == Signal.BUY

    def test_hold_within_bands(self) -> None:
        closes = [100.0] * 21
        bb = BollingerBands(window=20, num_std=2.0)
        assert bb.signal(_ohlcv(closes)) == Signal.HOLD

    def test_adds_bb_columns(self) -> None:
        closes = [100.0] * 21
        bb = BollingerBands(window=20, num_std=2.0)
        df = _ohlcv(closes)
        bb.signal(df)
        assert "BB_H" in df.columns
        assert "BB_L" in df.columns


@pytest.mark.unit
class TestMACD:
    def test_buy_when_fast_above_slow(self) -> None:
        macd = MACD(3, 6, 2)
        closes = [float(i) for i in range(1, 20)]
        assert macd.signal(_ohlcv(closes)) == Signal.BUY

    def test_sell_when_fast_below_slow(self) -> None:
        macd = MACD(3, 6, 2)
        closes = [float(20 - i) for i in range(20)]
        assert macd.signal(_ohlcv(closes)) == Signal.SELL


@pytest.mark.unit
class TestRSI:
    def test_hold_on_flat_prices(self) -> None:
        # No price movement → avg_gain == avg_loss → RS undefined → HOLD
        rsi = ResidualStrengthIndex(14, overbought=70.0, oversold=30.0)
        df = _ohlcv([100.0] * 30)
        assert rsi.signal(df) == Signal.HOLD


@pytest.mark.unit
class TestStochasticOscillation:
    def test_sell_when_overbought_and_crossing_down(self) -> None:
        # Price near the top of its range for the full window → overbought
        highs = [110.0] * 20
        lows = [90.0] * 20
        # Close near the top then slightly lower (K crosses below D)
        closes = [109.0] * 17 + [108.5, 108.0, 107.0]
        so = StochasticOscillation(
            k_period=14, d_period=3, overbought=80.0, oversold=20.0
        )
        result = so.signal(_ohlcv(closes, highs=highs, lows=lows))
        assert result == Signal.SELL

    def test_adds_k_and_d_columns(self) -> None:
        highs = [110.0] * 20
        lows = [90.0] * 20
        closes = [100.0] * 20
        so = StochasticOscillation(
            k_period=14, d_period=3, overbought=80.0, oversold=20.0
        )
        df = _ohlcv(closes, highs=highs, lows=lows)
        so.signal(df)
        assert "%K" in df.columns
        assert "%D" in df.columns
