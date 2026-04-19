import locale
import math
import random

from broker import Stock
from examples.brokers.mockbroker import MockBroker
from trader import DefaultStrategy, Trader
from trader.indicators import (
    MACD,
    BollingerBands,
    ResidualStrengthIndex,
    SimpleMovingAverage,
    StochasticOscillation,
)


def random_strat(
    overbought_range: tuple[int, int] = (60, 80),
    oversold_range: tuple[int, int] = (20, 40),
    rsi_range: tuple[int, int] = (10, 30),
    macd_range: tuple[int, int] = (5, 15),
    so_range: tuple[int, int] = (5, 15),
    bollinger_range: tuple[int, int] = (10, 30),
) -> DefaultStrategy:
    strat = DefaultStrategy()

    strat.add_indicator(SimpleMovingAverage(window=5))
    strat.add_indicator(SimpleMovingAverage(window=10))
    strat.add_indicator(SimpleMovingAverage(window=20))

    strat.add_indicator(
        BollingerBands(
            window=random.randint(*bollinger_range),
            num_std=random.uniform(1.5, 3.0),
        )
    )

    strat.add_indicator(
        StochasticOscillation(
            k_period=random.randint(*so_range),
            d_period=random.randint(*so_range),
            overbought=random.randint(*overbought_range),
            oversold=random.randint(*oversold_range),
        )
    )

    strat.add_indicator(
        ResidualStrengthIndex(
            window=random.randint(*rsi_range),
            overbought=random.randint(*overbought_range),
            oversold=random.randint(*oversold_range),
        )
    )

    fuzz_macd_k = random.randint(*macd_range)
    fuzz_macd_d = (fuzz_macd_k + 1) * 2
    fuzz_macd_t = int(math.ceil(fuzz_macd_k * 0.75))
    strat.add_indicator(
        MACD(k_period=fuzz_macd_k, d_period=fuzz_macd_d, t_period=fuzz_macd_t)
    )

    return strat


locale.setlocale(locale.LC_ALL, "")


def fuzz_strat(symbol: str, iterations: int = 100) -> DefaultStrategy:
    broker = MockBroker()

    stock = Stock(symbol, interval="1d")
    stock.load()

    # TODO: load a baseline strategy to beat from file once Strategy.load() is implemented
    best_strat = DefaultStrategy()
    best_score = 0.0

    for _ in range(iterations):
        strat = random_strat()
        trader = Trader(stock, broker, strat)
        trader.trade()

        # TODO: score the strategy on the back-test result (P&L, Sharpe, etc.)
        # and replace best_strat when score improves
        score = trader.capital
        if score > best_score:
            best_score = score
            best_strat = strat

    # TODO: persist best_strat once Strategy.save() is implemented
    return best_strat


if __name__ == "__main__":
    fuzz_strat("AAPL")
