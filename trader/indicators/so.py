import pandas as pd

from .indicator import Indicator, Signal


class StochasticOscillation(Indicator):
    """
    calculate stochastic oscillators
    tested with k_period=14 d_period=3 (days)
    https://www.alpharithms.com/stochastic-oscillator-in-python-483214/
    """

    def __init__(
        self, k_period: int, d_period: int, overbought: float, oversold: float
    ) -> None:
        self.window_k = k_period
        self.window_d = d_period
        self.overbought = overbought
        self.oversold = oversold

    def signal(self, df: pd.DataFrame) -> Signal:
        # Adds a "n_high" column with max value of previous k_period periods
        df["n_high"] = df["High"].rolling(self.window_k).max()

        # Adds an "n_low" column with min value of previous k_period periods
        df["n_low"] = df["Low"].rolling(self.window_k).min()

        # SO_K%: position of today's close within the k_period high/low range (0–100)
        df["SO_K%"] = (df["Close"] - df["n_low"]) * 100 / (df["n_high"] - df["n_low"])

        # SO_D%: smoothed signal line — SMA of SO_K% over d_period days
        df["SO_D%"] = df["SO_K%"].rolling(self.window_d).mean()

        k = df["SO_K%"].iloc[-1]
        d = df["SO_D%"].iloc[-1]

        # Overbought: both lines above threshold and %K has crossed back below %D
        if k > self.overbought and d > self.overbought and k < d:
            return Signal.SELL
        # Oversold: both lines below threshold and %K has crossed back above %D
        if k < self.oversold and d < self.oversold and k > d:
            return Signal.BUY

        return Signal.HOLD
