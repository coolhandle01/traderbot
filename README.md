# traderbot

A back-tested, fuzz-tested algorithmic trading bot with a pluggable strategy and broker layer.

## Structure

- `broker/` — broker abstraction (`Broker`), `Stock` (data loading via yfinance), and `Position`
- `trader/` — `Trader` engine, `Strategy`, and built-in indicators (SMA, BB, RSI, MACD, Stochastic)
- `examples/` — `MockBroker` for backtesting and a Trading 212 broker implementation

## Setup

```bash
pip install -e ".[dev]"
```

## Usage

See [`example.py`](example.py) for a full runnable example using `MockBroker`.

```python
broker = MockBroker()
stock = Stock("AAPL", interval="1d")
stock.load()

strat = Strategy()
strat.add_indicator(SimpleMovingAverage(20))
strat.add_indicator(MACD(12, 26, 9))

trader = Trader(stock, broker, strat)
```

## CI

Lint and type checks run on every push and PR via GitHub Actions. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
