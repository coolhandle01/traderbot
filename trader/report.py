import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from broker import Stock, StockAnalysis


class Report:
    def __init__(
        self,
        currency: str,
        oversold: float = 30.0,
        overbought: float = 70.0,
    ) -> None:
        self.currency = currency
        self.oversold = oversold
        self.overbought = overbought

    @staticmethod
    def graph_date(strtime: pd.Timestamp) -> str:
        return strtime.strftime("%Y-%m-%d")

    #
    # Candlestick Chart
    #
    def draw_candlestick_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:

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

        sma_5_line = {"color": "blueviolet", "width": 1}
        fig.add_trace(
            go.Scatter(name="SMA 5", x=df.index, y=df["SMA5"], opacity=0.7, line=sma_5_line),
            col=1,
            row=1,
        )

        sma_10_line = {"color": "blue", "width": 1}
        fig.add_trace(
            go.Scatter(name="SMA 10", x=df.index, y=df["SMA10"], opacity=0.7, line=sma_10_line),
            col=1,
            row=1,
        )

        sma_20_line = {"color": "navy", "width": 1}
        fig.add_trace(
            go.Scatter(name="SMA 20", x=df.index, y=df["SMA20"], opacity=0.7, line=sma_20_line),
            col=1,
            row=1,
        )

        bb_h_line = {"color": "pink", "width": 1}
        fig.add_trace(
            go.Scatter(name="BB Upper", x=df.index, y=df["BB_H"], opacity=0.7, line=bb_h_line),
            col=1,
            row=1,
        )

        bb_l_line = {"color": "pink", "width": 1}
        fig.add_trace(
            go.Scatter(name="BB Lower", x=df.index, y=df["BB_L"], opacity=0.7, line=bb_l_line),
            col=1,
            row=1,
        )

        return fig

    #
    # Stochastic Oscillation chart
    #
    def draw_so_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:

        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="black", col=1, row=2)
        fig.add_hline(y=self.oversold, line_width=1, line_dash="dot", line_color="grey", col=1, row=2)
        fig.add_hline(y=self.overbought, line_width=1, line_dash="dot", line_color="grey", col=1, row=2)
        fig.add_hline(y=100, line_width=1, line_dash="dash", line_color="black", col=1, row=2)

        fast_line = {"color": "pink", "width": 1}
        fig.add_trace(
            go.Scatter(name="fast", x=df.index, y=df["SO_K%"], opacity=0.7, line=fast_line),
            col=1,
            row=2,
        )

        slow_line = {"color": "cyan", "width": 1}
        fig.add_trace(
            go.Scatter(name="slow", x=df.index, y=df["SO_D%"], opacity=0.7, line=slow_line),
            col=1,
            row=2,
        )

        return fig

    #
    # RSI chart
    #
    def draw_rsi_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        rsi_line = {"color": "yellow", "width": 1}
        fig.add_trace(
            go.Scatter(name="RSI", x=df.index, y=df["%RSI"], opacity=0.7, line=rsi_line),
            col=1,
            row=2,
        )
        return fig

    #
    # MACD chart
    #
    def draw_macd_chart(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        colors = np.where(df["MACD_H"] < 0, "tomato", "olive")

        fig.add_trace(
            go.Bar(x=df.index, y=df["MACD_H"], name="histogram", marker_color=colors),
            col=1,
            row=3,
        )

        macd_line = {"color": "purple", "width": 1}
        fig.add_trace(
            go.Scatter(name="MACD", x=df.index, y=df["MACD"], opacity=0.7, line=macd_line),
            col=1,
            row=3,
        )

        macd_signal_line = {"color": "darkorange", "width": 1}
        fig.add_trace(
            go.Scatter(name="MACD Signal", x=df.index, y=df["MACD_S"], opacity=0.7, line=macd_signal_line),
            col=1,
            row=3,
        )

        return fig

    #
    # Stock Performance Metrics table
    #
    @staticmethod
    def draw_stock_analysis(fig: go.Figure, analysis: StockAnalysis) -> go.Figure:
        metrics = ["Annualized Return", "Volatility", "Sharpe Ratio", "Max Drawdown"]
        scores = [
            analysis.annualized_return,
            analysis.volatility,
            analysis.sharpe_ratio,
            analysis.max_drawdown,
        ]

        header = {"values": ["Metric", "Score"], "line_color": "darkslategray", "fill_color": "lightskyblue", "align": "left"}
        cells = {"values": [metrics, scores], "line_color": "darkslategray", "fill_color": "lightcyan", "align": "left"}

        fig.add_trace(go.Table(header=header, cells=cells), col=1, row=4)

        return fig

    def show_graph(self, stock: Stock, html: bool = False) -> go.Figure:
        symbol = stock.symbol
        df = stock.history
        print(f"Graphing Analysis for {symbol}")

        start = self.graph_date(df.index.min())
        end = self.graph_date(df.index.max())
        dt_all = pd.date_range(start=start, end=end)

        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]

        fig = make_subplots(
            rows=4,
            cols=1,
            shared_xaxes=True,
            row_heights=[0.4, 0.2, 0.2, 0.2],
            subplot_titles=["OHLC", "Stochastic Oscillation / RSI", "MACD", "Performance"],
        )

        fig.update_xaxes(rangebreaks=[{"values": dt_breaks}], col=1, row=1)

        fig = self.draw_candlestick_chart(fig, df)

        fig.update_yaxes(range=[-10, 110], col=1, row=2)
        fig = self.draw_so_chart(fig, df)
        fig = self.draw_rsi_chart(fig, df)

        fig.update_yaxes(range=[-10, 10], col=1, row=3)
        fig = self.draw_macd_chart(fig, df)

        analysis = StockAnalysis(stock)
        fig = self.draw_stock_analysis(fig, analysis)

        layout = go.Layout(
            title=f"{symbol} Analysis",
            yaxis_title=f"Price ({self.currency})",
            xaxis_title="Time",
            plot_bgcolor="#efefef",
            font_family="Monospace",
            font_color="#323232",
            font_size=12,
            xaxis={"rangeslider": {"visible": False}},
        )
        fig.update_layout(layout)

        if html:
            fig.write_html(f".portfolio/{symbol}/history.html")

        return fig
