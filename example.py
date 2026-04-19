import asyncio
import locale

from dotenv import load_dotenv

from broker import Stock
from examples.brokers.mockbroker import MockBroker
from trader import DefaultStrategy, Trader
from trader.indicators import (
    MACD,
    BollingerBands,
    EMACrossover,
    ResidualStrengthIndex,
    SimpleMovingAverage,
    StochasticOscillation,
)


async def main() -> None:

    load_dotenv()
    locale.setlocale(locale.LC_ALL, "")

    symbol = "AAPL"
    overbought = 70
    oversold = 30

    broker = MockBroker()
    stock = Stock(symbol, interval="1d")
    stock.load()

    strat = DefaultStrategy()
    strat.add_indicator(SimpleMovingAverage(5))
    strat.add_indicator(SimpleMovingAverage(10))
    strat.add_indicator(SimpleMovingAverage(20))
    strat.add_indicator(BollingerBands(20, 2))
    strat.add_indicator(EMACrossover(10, 20, overbought=overbought, oversold=oversold))
    strat.add_indicator(
        StochasticOscillation(14, 3, overbought=overbought, oversold=oversold)
    )
    strat.add_indicator(
        ResidualStrengthIndex(14, overbought=overbought, oversold=oversold)
    )
    strat.add_indicator(MACD(12, 26, 9))

    trader = Trader(stock, broker, strat)

    while True:
        stock.update()
        trader.trade()
        await asyncio.sleep(60)


asyncio.run(main())
