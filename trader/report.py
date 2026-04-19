import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategy import Strategy


class Report:
    def __init__(self, strat: Strategy, currency: str) -> None:
        self.strat = strat
        self.currency = currency

    @staticmethod
    def graph_date(strtime: pd.Timestamp) -> str:
        return strtime.strftime("%Y-%m-%d")

    #
    # Candlestick Chart
    #
    def draw_candlestick_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:

        # add OHLC candlesticks
        fig.add_trace(
            go.Candlestick(
                name="OHLC",
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                increasing_line_color="green",
                decreasing_line_color="red",
            ),
            col=1,
            row=1,
        )

        # add moving average traces
        sma_5_line = {"color": "blueviolet", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="SMA 5",
                x=df.index,
                y=df["SMA5"],
                opacity=0.7,
                line=sma_5_line,
            ),
            col=1,
            row=1,
        )

        sma_10_line = {"color": "blue", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="SMA 10",
                x=df.index,
                y=df["SMA10"],
                opacity=0.7,
                line=sma_10_line,
            ),
            col=1,
            row=1,
        )

        sma_20_line = {"color": "navy", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="SMA 20",
                x=df.index,
                y=df["SMA20"],
                opacity=0.7,
                line=sma_20_line,
            ),
            col=1,
            row=1,
        )

        # add bollinger bands
        bb_h_line = {"color": "pink", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="BB Upper",
                x=df.index,
                y=df["BB_H"],
                opacity=0.7,
                line=bb_h_line,
            ),
            col=1,
            row=1,
        )

        bb_l_line = {"color": "pink", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="BB Lower",
                x=df.index,
                y=df["BB_L"],
                opacity=0.7,
                line=bb_l_line,
            ),
            col=1,
            row=1,
        )

        return fig

    #
    # Stochastic Oscillation chart
    #
    def draw_so_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:

        # bounds: lower, oversold, overbought, upper
        fig.add_hline(
            y=0, line_width=1, line_dash="dash", line_color="black", col=1, row=2
        )
        fig.add_hline(
            y=self.strat.oversold,
            line_width=1,
            line_dash="dot",
            line_color="grey",
            col=1,
            row=2,
        )
        fig.add_hline(
            y=self.strat.overbought,
            line_width=1,
            line_dash="dot",
            line_color="grey",
            col=1,
            row=2,
        )
        fig.add_hline(
            y=100, line_width=1, line_dash="dash", line_color="black", col=1, row=2
        )

        # Fast Signal (%k)
        fast_line = {"color": "pink", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="fast", x=df.index, y=df["%K"], opacity=0.7, line=fast_line
            ),
            col=1,
            row=2,
        )

        # Slow signal (%d)
        slow_line = {"color": "cyan", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="slow", x=df.index, y=df["%D"], opacity=0.7, line=slow_line
            ),
            col=1,
            row=2,
        )

        return fig

    #
    # MACD chart
    #
    def draw_macd_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        # Colorize the histogram values
        colors = np.where(df["MACD_H"] < 0, "tomato", "olive")

        # Plot the histogram
        fig.add_trace(
            go.Bar(x=df.index, y=df["MACD_H"], name="histogram", marker_color=colors),
            col=1,
            row=3,
        )

        # Slow Signal (D)
        macd_line = {"color": "purple", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="MACD", x=df.index, y=df["MACD"], opacity=0.7, line=macd_line
            ),
            col=1,
            row=3,
        )

        # Fast Signal (K)
        macd_signal_line = {"color": "darkorange", "width": 1}
        fig.add_trace(
            go.Scatter(
                name="MACD Signal",
                x=df.index,
                y=df["MACD_S"],
                opacity=0.7,
                line=macd_signal_line,
            ),
            col=1,
            row=3,
        )

        return fig

    def show_graph(self, symbol: str, df: pd.DataFrame) -> go.Figure:
        print(f"Graphing Analysis for {symbol}")
        # remove empty dates

        # build complete timeline from start date to end date
        start = self.graph_date(df.index.min())
        end = self.graph_date(df.index.max())
        dt_all = pd.date_range(start=start, end=end)

        # retrieve the dates that ARE in the original dataset
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]

        # define dates with missing values
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]

        # Create our primary chart
        # the rows/cols arguments tell plotly we want three figures
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=["OHLC", "Stochastic Oscillation", "MACD"],
        )

        # hide x-axis dates with no values
        fig.update_xaxes(rangebreaks=[{"values": dt_breaks}], col=1, row=1)

        # OHLC
        fig = self.draw_candlestick_chart(fig, df)

        # Extend y-axis for plot 2
        fig.update_yaxes(range=[-10, 110], col=1, row=2)

        # Stochastic Oscillation
        fig = self.draw_so_chart(fig, df)

        # Extend y-axis for plot 3
        fig.update_yaxes(range=[-10, 10], col=1, row=3)

        # MACD
        fig = self.draw_macd_chart(fig, df)

        #
        # configure the graph layout
        #
        layout = go.Layout(
            title=f"{symbol} Analysis",
            yaxis_title=f"Price ({self.currency})",
            xaxis_title="Time",
            # Make it pretty
            plot_bgcolor="#efefef",
            # Font Families
            font_family="Monospace",
            font_color="#323232",
            font_size=12,
            xaxis={"rangeslider": {"visible": False}},
        )
        fig.update_layout(layout)

        # show the figure
        # fig.show()
        return fig
