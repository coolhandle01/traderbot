import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Report:
    def __init__(self) -> None:
        pass

    def graph_date(strtime):
        t = pd.Timestamp(ts_input=strtime)
        return t.strftime('%Y-%m-%d')

    #
    # Candlestick Chart
    #
    def draw_candlestick_chart(self, fig: go.Figure, df: pd.DataFrame):

        # add OHLC candlesticks
        fig.add_trace(go.Candlestick(name='OHLC', x=self.df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='green',
                    decreasing_line_color='red'),
                    col=1,
                    row=1)        

        # add moving average traces
        sma_5_line=dict(color='blueviolet', width=1)
        fig.add_trace(go.Scatter(name='SMA 5', x=self.df.index, y=df['SMA5'], opacity=0.7, line=sma_5_line),
                    col=1,
                    row=1)

        sma_10_line=dict(color='blue', width=1)
        fig.add_trace(go.Scatter(name='SMA 10', x=self.df.index, y=df['SMA10'], opacity=0.7, line=sma_10_line),
                    col=1,
                    row=1)

        sma_20_line=dict(color='navy', width=1)
        fig.add_trace(go.Scatter(name='SMA 20', x=self.df.index, y=df['SMA20'], opacity=0.7, line=sma_20_line),
                    col=1,
                    row=1)

        
        # add bollinger bands
        bb_h_line=dict(color='pink', width=1)
        fig.add_trace(go.Scatter(name='BB Upper', x=self.df.index, y=df['BB_H'], opacity=0.7, line=bb_h_line),
                    col=1,
                    row=1)
        
        bb_l_line=dict(color='pink', width=1)
        fig.add_trace(go.Scatter(name='BB Lower', x=self.df.index, y=df['BB_L'], opacity=0.7, line=bb_l_line),
                    col=1,
                    row=1)
        
        return fig

    #
    # Stochastic Oscillation chart
    #
    def draw_so_chart(self, fig: go.Figure, df: pd.DataFrame):

        # bounds: lower, oversold, overbought, upper
        fig.add_hline(y=0,                      line_width=1, line_dash="dash", line_color="black", col=1, row=2)
        fig.add_hline(y=self.strat.oversold,   line_width=1, line_dash="dot",  line_color="grey",  col=1, row=2)
        fig.add_hline(y=self.strat.overbought, line_width=1, line_dash="dot",  line_color="grey",  col=1, row=2)
        fig.add_hline(y=100,                    line_width=1, line_dash="dash", line_color="black", col=1, row=2)
        
        # Fast Signal (%k)
        fast_line=dict(color='pink', width=1)
        fig.add_trace(go.Scatter(name='fast', x=self.df.index, y=df['%K'], opacity=0.7, line=fast_line),
                    col=1,
                    row=2)

        # Slow signal (%d)
        slow_line=dict(color='cyan', width=1)
        fig.add_trace(go.Scatter(name='slow', x=self.df.index, y=df['%D'], opacity=0.7, line=slow_line),
                    col=1,
                    row=2)

        # add RSI traces
        # rsi_line=dict(color='yellow', width=1)
        # fig.add_trace(go.Scatter(name='RSI', x=self.df.index, y=df['%RSI'], opacity=0.7, line=rsi_line),
        #               col=1,
        #               row=2)
        
        return fig

    #
    # MACD chart
    #
    def draw_macd_chart(self, fig: go.Figure, df: pd.DataFrame):
        # # bounds: lower, oversold, overbought, upper
        # fig.add_hline(y=-10, line_width=1, line_dash="dash", line_color="darkgrey", col=1, row=3)
        # fig.add_hline(y=-8,  line_width=1, line_dash="dot",  line_color="pink", col=1, row=3)
        # fig.add_hline(y=8,   line_width=1, line_dash="dot",  line_color="pink", col=1, row=3)
        # fig.add_hline(y=10,  line_width=1, line_dash="dash", line_color="darkgrey", col=1, row=3)
        
        # Colorize the histogram values
        colors = np.where(df['MACD_H'] < 0, 'tomato', 'olive')

        # Plot the histogram
        fig.add_trace(go.Bar(x=self.df.index, y=df['MACD_H'], name='histogram', marker_color=colors), 
                    col=1,
                    row=3)

        # Slow Signal (D)
        macd_line=dict(color='purple', width=1)
        fig.add_trace(go.Scatter(name='MACD', x=self.df.index, y=df['MACD'], opacity=0.7, line=macd_line),
                    col=1,
                    row=3)

        # Fast Signal (K)
        macd_signal_line=dict(color='darkorange', width=1)
        fig.add_trace(go.Scatter(name='MACD Signal', x=self.df.index, y=df['MACD_S'], opacity=0.7, line=macd_signal_line),
                    col=1,
                    row=3)
        
        return fig

    def show_graph(self, symbol: str, df: pd.DataFrame) -> go.Figure:
        print(f'Graphing Analysis for {symbol}')
        # remove empty dates

        # build complete timeline from start date to end date
        start = self.graph_date(df['Date'].min())
        end = self.graph_date(df['Date'].max())
        dt_all = pd.date_range(start=start, end=end)

        # retrieve the dates that ARE in the original datset
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(self.df.index)]

        # define dates with missing values
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

        # Create our primary chart
        # the rows/cols arguments tell plotly we want three figures
        fig = make_subplots(rows=3, cols=1, 
                            shared_xaxes=True, 
                            row_heights=[0.5, 0.25, 0.25], 
                            subplot_titles=['OHLC', 'Stochastic Oscillation', 'MACD']
                            )
        
        # hide x-axis dates with no values
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)], col=1, row=1)   
        
        # OHLC
        fig = self.draw_candlestick_chart(self, fig, df)

        # Extend y-axis for plot 2
        fig.update_yaxes(range=[-10, 110], col=1, row=2)

        # Stochastic Oscillation
        fig = self.draw_so_chart(self, fig)

        # Extend y-axis for plot 3
        fig.update_yaxes(range=[-10, 10], col=1, row=3)

        # MACD
        fig = self.draw_macd_chart(self, fig)

        #
        # configure the graph layout
        #
        layout = go.Layout(
            title=f'{symbol} Analysis',
            yaxis_title=f'Price ({self.currency})',
            xaxis_title='Time',
            # Make it pretty
            plot_bgcolor='#efefef',
            # Font Families
            font_family='Monospace',
            font_color='#323232',
            font_size=12,
            xaxis=dict(
                rangeslider=dict(
                    visible=False
                )
            )
        )
        fig.update_layout(layout)

        # show the figure
        #fig.show()
        return fig
