import locale
import random
import math

from examples.brokers.mockbroker import MockBroker
from broker import Stock
from trader import Trader, Strategy
from trader.indicators import StochasticOscillation, BollingerBands, ResidualStrengthIndex, MACD, SimpleMovingAverage

def random_strat(overbought_range=(60, 80), 
               oversold_range=(20, 40), 
               rsi_range=(10, 30), 
               macd_range=(5, 15), 
               so_range=(5, 15), 
               bollinger_range=(10, 30)) -> Strategy:
    strat = Strategy()

    strat.add_indicator(indicator=SimpleMovingAverage(window=5))
    strat.add_indicator(indicator=SimpleMovingAverage(window=10))
    strat.add_indicator(indicator=SimpleMovingAverage(window=20))

    strat.add_indicator(indicator=BollingerBands(window=random.randint(*bollinger_range), num_std=random.uniform(1.5, 3.0)))

    strat.add_indicator(indicator=StochasticOscillation(k_period=random.randint(*so_range), d_period=random.randint(*so_range), overbought=random.randint(*overbought_range), oversold=random.randint(*oversold_range)))
    strat.add_indicator(indicator=ResidualStrengthIndex(window=random.randint(*rsi_range), overbought=random.randint(*overbought_range), oversold=random.randint(*oversold_range)))

    fuzz_macd_k = random.randint(*macd_range)
    fuzz_macd_d = (fuzz_macd_k + 1) * 2
    fuzz_macd_t = math.fabs(fuzz_macd_k * 0.75)
    strat.add_indicator(indicator=MACD(k_period=fuzz_macd_k, d_period=fuzz_macd_d, t_period=fuzz_macd_t))

    return strat


locale.setlocale(locale.LC_ALL, '')

def fuzz_strat(symbol: str, iterations: int) -> Strategy:

    broker = MockBroker()

    stock = Stock(symbol, interval='1d')
    stock.load()

    best_strat = Strategy()
    with open('./baseline.strat', 'r') as stream:
        best_strat.load(stream)

    for _ in iterations:
        strat = random_strat()
        
        trader = Trader(stock, broker, strat)
        trader.trade()

        analysis = trader.analysis

        # TODO: test analysis
        if analysis is not None:
            best_strat = strat

    with open('./best.strat', 'w') as stream:
        best_strat.save(stream)

fuzz_strat('AAPL')