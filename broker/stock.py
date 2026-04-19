"""
Stock.py
"""

import os

import numpy as np
import pandas as pd
import yfinance as yf


class Stock:
    """
    Represents the history of a given ticker symbol at a given interval
    """

    def __init__(self, symbol: str, interval: str) -> None:
        self.symbol = symbol
        self.interval = interval
        self.history: pd.DataFrame = pd.DataFrame()

        self.archive = f"history/{self.symbol}/{self.interval}.csv"

    def load(self) -> None:
        """load a pandas dataframe for the history of this ticker from local file"""
        print(f"loading history for {self.symbol}")

        if os.path.isfile(self.archive) is False:
            self.download()

        self.history = pd.read_csv(self.archive, index_col=0, parse_dates=True)

    def download(self) -> None:
        """save a pandas dataframe for the history of this ticker to local file"""
        print(f"downloading history for {self.symbol}")

        os.makedirs(os.path.dirname(self.archive), exist_ok=True)

        history = yf.download(self.symbol, period="max", interval=self.interval)
        history.to_csv(self.archive)

    def update(self) -> None:
        """append the latest events at this interval to the history"""
        print(f"updating history for {self.symbol}")
        last_downloaded = self.history.index.max() if not self.history.empty else None
        events = yf.download(self.symbol, start=last_downloaded, interval=self.interval)
        if not self.history.empty:
            events = events.loc[
                ~events.index.isin(self.history.index)
            ]  # filter out duplicates

        self.history = pd.concat([self.history, events])
        self.history.to_csv(self.archive)

    def copy(self) -> pd.DataFrame:
        """return a copy of the loaded history"""
        return self.history.copy(deep=True)  # type: ignore[no-any-return]

    def tail(self) -> pd.DataFrame:
        """return a copy of the last event of the loaded history"""
        return self.history.tail(1).copy(deep=True)  # type: ignore[no-any-return]


# https://tradewithpython.com/portfolio-analysis-using-python#heading-5-analysis
class StockAnalysis:
    def __init__(
        self, stock: Stock, column: str = "Close", interval: int = 1, window: int = 252
    ):
        self.price_history: pd.Series = stock.history[column]
        self.daily_returns = self._calculate_daily_returns(interval)
        self.annualized_return = self._calculate_annualized_return(window)
        self.volatility = self._calculate_volatility(window)
        self.sharpe_ratio = self._calculate_sharpe_ratio(window)
        self.max_drawdown = self._calculate_max_drawdown()

    def _calculate_daily_returns(self, interval: int) -> pd.Series:
        return self.price_history.pct_change(interval).dropna()

    def _calculate_annualized_return(self, window: int) -> float:
        return float((1 + self.daily_returns.mean()) ** window - 1)

    def _calculate_volatility(self, window: int) -> float:
        return float(self.daily_returns.std() * np.sqrt(window))

    def _calculate_sharpe_ratio(self, window: int) -> float:
        return float(
            self.daily_returns.mean() / self.daily_returns.std() * np.sqrt(window)
        )

    def _calculate_max_drawdown(self) -> float:
        cumulative_returns = (1 + self.daily_returns).cumprod()
        drawdown = (cumulative_returns / cumulative_returns.cummax()) - 1
        return float(drawdown.min())


class PortfolioAnalysis:
    def __init__(
        self, symbols: list[str] | None = None, interval: int = 1, window: int = 252
    ):
        if symbols is None:
            symbols = ["AAPL"]
        self.symbols = symbols

        self.price_matrix = pd.DataFrame()
        for i, symbol in enumerate(self.symbols):
            stock = Stock(symbol, interval="1d")
            stock.load()

            price_history = stock.history.filter(["Close"])
            price_history = price_history.rename(columns={"Close": symbol})
            if i == 0:
                self.price_matrix = price_history
            else:
                self.price_matrix = self.price_matrix.join(price_history)

        self.correlation = self.price_matrix.corr(method="pearson")

        self.simple_returns = self.price_matrix.pct_change(interval).dropna()

        self.average_simple_returns = self.simple_returns.mean()

        # Annualized Standard Deviation (252 trading days)
        self.asd = self.simple_returns.std() * np.sqrt(window) * 100

        # return per unit of risk
        self.perunit = self.average_simple_returns / self.asd

        # cumulative simple return
        self.dsrc = (self.simple_returns + 1).cumprod()
