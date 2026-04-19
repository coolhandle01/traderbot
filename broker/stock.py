"""
Stock.py
"""

import os

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

        if os.path.isdir(self.archive) is False:
            os.mkdir(self.archive)

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
