import pandas as pd
from indicator import Indicator, Signal


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

        # fast
        # Uses the min/max values to calculate the %k (as a percentage)
        df["SO_K%"] = (df["Close"] - df["n_low"]) * 100 / (df["n_high"] - df["n_low"])

        # slow
        # Uses the %k to calculates a SMA over the past 3 values of %k
        df["SO_D%"] = df["%K"].rolling(self.window_d).mean()

        # this is probably crude:
        # Overbought status
        if (
            df["SO_K%"].iloc[-1] > self.overbought
            and df["SO_D%"].iloc[-1] > self.overbought
            and df["SO_K%"].iloc[-1] < df["SO_D%"].iloc[-1]
        ):
            return Signal.SELL
        # Oversold status
        elif (
            df["SO_K%"].iloc[-1] < self.oversold
            and df["SO_D%"].iloc[-1] < self.oversold
            and df["SO_K%"].iloc[-1] > df["SO_D%"].iloc[-1]
        ):
            return Signal.BUY
        # Something in the middle
        else:
            return Signal.HOLD
