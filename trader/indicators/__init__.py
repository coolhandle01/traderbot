"""
Trader
"""

from .bb import BollingerBands
from .crossover import EMACrossover, SMACrossover
from .indicator import Indicator
from .ma import SimpleMovingAverage
from .macd import MACD
from .rsi import ResidualStrengthIndex
from .signal import Signal
from .so import StochasticOscillation

__all__ = [
    "Signal",
    "Indicator",
    "BollingerBands",
    "SimpleMovingAverage",
    "SMACrossover",
    "EMACrossover",
    "MACD",
    "ResidualStrengthIndex",
    "StochasticOscillation",
]


# What is a Bullish Market?
# A bullish market, often referred to simply as a "bull market," is characterized by rising prices and a general sense of optimism among investors. In a bull market, the demand for securities outstrips supply, leading to higher prices. This positive sentiment is typically fueled by strong economic indicators, corporate earnings growth, and investor confidence.

# Key Characteristics of a Bullish Market:
# - Rising Prices: The most defining feature of a bull market is the sustained increase in the prices of stocks and other securities.
# - High Investor Confidence: Investors believe that the market will continue to perform well, leading to increased buying activity.
# - Strong Economic Indicators: Indicators such as GDP growth, low unemployment rates, and high consumer spending often accompany bull markets.
# - Increased Trading Volume: Higher trading volumes are common as more investors participate in the market, seeking to capitalize on rising prices.

# Strategies for Navigating a Bullish Market:
# - Buy and Hold: In a bull market, buying stocks and holding them for the long term can be a profitable strategy as prices are expected to rise.
# - Growth Investing: Focus on investing in companies with strong growth potential. These companies are likely to benefit the most from a rising market.
# - Momentum Trading: Take advantage of the upward price momentum by buying stocks that are already performing well and selling them as they continue to rise.
# - Diversification: While the overall market is performing well, diversifying your portfolio can help manage risk and capture gains across various sectors.

# What is a Bearish Market?
# A bearish market, or "bear market," is characterized by falling prices and widespread pessimism among investors. In a bear market, the supply of securities exceeds demand, leading to declining prices. Bear markets are often triggered by economic downturns, negative corporate earnings, and investor fear.

# Key Characteristics of a Bearish Market:
# - Falling Prices: The most defining feature of a bear market is the sustained decline in the prices of stocks and other securities.
# - Low Investor Confidence: Investors lose confidence in the market's ability to perform well, leading to increased selling activity.
# - Weak Economic Indicators: Indicators such as declining GDP, rising unemployment rates, and reduced consumer spending often accompany bear markets.
# - Decreased Trading Volume: Lower trading volumes are common as investors become more cautious and risk-averse.

# Strategies for Navigating a Bearish Market:
# - Defensive Investing: Focus on investing in sectors that are less sensitive to economic cycles, such as utilities, healthcare, and consumer staples.
# - Short Selling: Short selling involves borrowing shares to sell at the current price and buying them back at a lower price, profiting from the decline.
# - Hedging: Use hedging strategies, such as options and futures, to protect your portfolio from significant losses.
# - Dollar-Cost Averaging: Invest a fixed amount of money at regular intervals, regardless of market conditions. This strategy helps reduce the impact of market volatility.

# Comparing Bullish and Bearish Markets
# Understanding the differences between bullish and bearish markets is essential for developing effective investment strategies. Here's a quick comparison:
# - Market Sentiment: Bullish markets are driven by optimism, while bearish markets are driven by pessimism.
# - Price Movement: Prices rise in bullish markets and fall in bearish markets.
# - Investor Behavior: Investors tend to buy in bullish markets and sell in bearish markets.
# - Economic Indicators: Bullish markets often align with strong economic indicators, whereas bearish markets align with weak economic indicators.
