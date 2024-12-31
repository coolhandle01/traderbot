import os
import locale
import asyncio
from dotenv import load_dotenv

from broker import Stock
from trader import Trader, Strategy
from trader.indicators import StochasticOscillation, BollingerBands, ResidualStrengthIndex, MACD, SimpleMovingAverage

from examples.brokers.mockbroker import MockBroker

async def main():

    load_dotenv()
    locale.setlocale(locale.LC_ALL, '')

    symbol = 'AAPL'

    broker = MockBroker()
    stock = Stock(symbol, interval='1d')
    stock.load()

    strat = Strategy()
    overbought = 70
    oversold = 30

    strat.add_indicator(indicator=SimpleMovingAverage(5))
    strat.add_indicator(indicator=SimpleMovingAverage(10))
    strat.add_indicator(indicator=SimpleMovingAverage(20))
    strat.add_indicator(indicator=BollingerBands(20, 2))

    strat.add_indicator(indicator=StochasticOscillation(14, 3, overbought=overbought, oversold=oversold))
    strat.add_indicator(indicator=ResidualStrengthIndex(14, overbought=overbought, oversold=oversold))
    strat.add_indicator(indicator=MACD(12, 26, 9))

    trader = Trader(stock, broker, strat)

    while True:
        stock.update()
        trader.trade()

        await asyncio.sleep(60)

asyncio.run(main())
