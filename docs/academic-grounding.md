# Academic grounding

This document grounds traderbot's techniques in the primary literature - the
papers and books that introduced or rigorously tested them - rather than the
practitioner explainer blogs the code comments currently link to. Those blogs
(Investopedia, alpharithms, StockCharts) are fine for "how do I compute this in
pandas"; they are not evidence that a technique *works*. This file is the
evidence, including the parts that are uncomfortable.

It doubles as an honest reality check. traderbot is a technical-analysis
backtester, and the academic consensus on technical analysis in liquid equity
markets - net of trading costs and net of the statistical bias introduced by
searching over many rules - is skeptical. That does not make the project
pointless: it makes the project's *methodology* the thing that matters. A
strategy that looks good in-sample is worthless; a measurement framework that
can tell the difference between a real edge and a lucky backtest is the actual
prize. Read the "Methodological risks" section as the design brief, not as a
verdict.

How to read each entry: **what traderbot does**, **where** (the file),
**the primary source**, and **what the evidence actually says**.

## 1. The null hypothesis: market efficiency

Everything in `trader/indicators/` consumes only past prices and volumes. The
weak form of the Efficient Market Hypothesis says exactly that information set
cannot be used to earn risk-adjusted excess returns, because prices already
reflect it.

- Fama, E. F. (1970). "Efficient Capital Markets: A Review of Theory and
  Empirical Work." *Journal of Finance* 25(2):383-417.
  [doi:10.1111/j.1540-6261.1970.tb00518.x](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1970.tb00518.x)

EMH is a null hypothesis, not a law - it is contested and markets are not
perfectly efficient - but it is the bar every signal in this repo is implicitly
claiming to clear. State that claim honestly: a strategy that beats buy-and-hold
in a backtest is asserting a weak-form-EMH violation, which is a strong claim
that demands strong evidence (Sections 5-6).

## 2. The indicators

Each indicator file currently cites a tutorial site. Here are the primary
sources, and what testing them has shown.

**Moving averages and MA crossovers** - `trader/indicators/ma.py`,
`trader/indicators/crossover.py` (`SMACrossover`, `EMACrossover`).

- Brock, W., Lakonishok, J., & LeBaron, B. (1992). "Simple Technical Trading
  Rules and the Stochastic Properties of Stock Returns." *Journal of Finance*
  47(5):1731-1764.
  [doi:10.1111/j.1540-6261.1992.tb04681.x](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x)

  The landmark *favourable* result: moving-average and trading-range-break rules
  had predictive power on the Dow 1897-1986. This is the paper proponents cite.
  Read the next entry before relying on it.

**Bollinger Bands** - `trader/indicators/bb.py`.

- Bollinger, J. (2001). *Bollinger on Bollinger Bands.* McGraw-Hill.
  ISBN 978-0071373685. The primary source from the indicator's originator; note
  Bollinger himself frames the bands as relative-volatility context, not a
  standalone buy/sell trigger.

**MACD** - `trader/indicators/macd.py`.

- Appel, G. (2005). *Technical Analysis: Power Tools for Active Investors.*
  FT Prentice Hall. ISBN 978-0131479029. Appel introduced MACD; this is the
  primary reference for the construction the file implements.

**RSI** - `trader/indicators/rsi.py`. The class is named
`ResidualStrengthIndex`; the indicator is the *Relative* Strength Index, and
the source is unambiguous:

- Wilder, J. W. (1978). *New Concepts in Technical Trading Systems.* Trend
  Research. ISBN 978-0894590276. The book that introduced RSI (and ATR, ADX,
  Parabolic SAR) and the Wilder smoothing the code implements in its one
  justified loop.

**Stochastic Oscillator** - `trader/indicators/so.py`. Attributed to George C.
Lane (popularised from the 1950s onward); it has no single peer-reviewed primary
source, which is itself worth noting - much of classical TA is practitioner
folklore, not derived results.

**What the evidence actually says about indicators as a class:**

- Sullivan, R., Timmermann, A., & White, H. (1999). "Data-Snooping, Technical
  Trading Rule Performance, and the Bootstrap." *Journal of Finance*
  54(5):1647-1691.
  [doi:10.1111/0022-1082.00163](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00163)
  ([free PDF](https://www.kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)).
  Re-ran Brock et al. (1992) over a universe of ~7,800 rules with White's
  bootstrap to correct for the fact that the "best" rule was *chosen* from many.
  The apparent profitability shrank sharply once data-snooping was accounted for
  and did not persist out of sample. This is the single most important paper for
  this repo: it is the same mistake `scripts/fuzz-strat.py` is built to make.

- Lo, A. W., Mamaysky, H., & Wang, J. (2000). "Foundations of Technical
  Analysis." *Journal of Finance* 55(4):1705-1765.
  [doi:10.1111/0022-1082.00265](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00265)
  ([NBER w7613](https://www.nber.org/papers/w7613)). A relatively favourable,
  rigorous take: some chart patterns carry modest incremental information.

- Park, C.-H., & Irwin, S. H. (2007). "What Do We Know About the Profitability
  of Technical Analysis?" *Journal of Economic Surveys* 21(4):786-826.
  [doi:10.1111/j.1467-6419.2007.00519.x](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-6419.2007.00519.x).
  The survey. Bottom line: early studies found profits, but in *equities* and
  especially *after about 1990* and *after costs*, the evidence for technical
  trading profitability is weak. Profits were more durable in FX and futures
  than in stocks - which is the market traderbot targets.

The honest summary: there is a respectable case that simple TA rules carried
information historically, and a stronger case that most of that apparent edge
was data-snooping and/or eroded by costs and arbitrage once published. Treat any
single indicator as a weak, costly prior, not a money printer.

## 3. The benchmark strategies

traderbot benchmarks active strategies against passive ones - which is exactly
the right scientific control.

**Buy-and-hold** - `trader/strategies/buyandhold.py` (its docstring already
calls it "the floor every active strategy must beat"). That instinct is well
supported:

- The S&P Dow Jones Indices [SPIVA Scorecards](https://www.spglobal.com/spdji/en/research-insights/spiva/)
  document that a large majority of active equity managers underperform their
  index benchmark over 10-15 year horizons. Beating buy-and-hold net of costs is
  hard for professionals; it is the correct, demanding null for an active
  strategy.

**Dollar-cost averaging** - `trader/strategies/dca.py`. DCA is widely
recommended, but as a *return*-maximiser it is known to be suboptimal:

- Constantinides, G. M. (1979). "A Note on the Suboptimality of Dollar-Cost
  Averaging as an Investment Policy." *Journal of Financial and Quantitative
  Analysis* 14(2):443-450.
  [Cambridge Core](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/note-on-the-suboptimality-of-dollarcost-averaging-as-an-investment-policy/0C483B96429655B24F34FB628CF9CEEB).
- Vanguard (2012, updated 2023). "Dollar-cost averaging just means taking risk
  later."
  [Vanguard research](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf).
  Empirically, lump-sum investing beats DCA roughly two-thirds of the time
  because markets drift up. DCA's value is behavioural (regret/risk reduction),
  not expected return. So DCA is a fair *behavioural* benchmark, but do not be
  surprised when it loses to B&H on raw return - that is the expected result,
  not a bug.

**Swing / mean reversion** - `trader/strategies/swing.py` (buy below a rolling
high, sell above a rolling low). This is a short-horizon mean-reversion bet.
Short-horizon reversal is one of the better-documented anomalies, but it is also
where transaction costs bite hardest (it trades often), which is why
`Swing.configure()` raising its threshold above the round-trip fee is not
optional polish - it is the difference between the strategy being testable and
being a fee pump (Section 4).

## 4. Transaction costs are first-order, and the code is right to model them

`Trader.sell()` nets fees and stamp duty before deciding, and fee-aware
strategies gate signals on round-trip cost. This is methodologically important,
not incidental: the technical-analysis profits in Brock et al. (1992) largely
*disappear* once realistic costs are subtracted (a central critique in Sullivan
et al. 1999 and Park & Irwin 2007). UK stamp duty on share purchases (0.5%,
[HMRC](https://www.gov.uk/tax-buy-shares)) alone is enough to sink a
high-turnover rule. Keep costs in every backtest; a frictionless backtest is not
evidence of anything. The current `MockBroker` reports zero fees, which is fine
for unit tests but means a zero-fee backtest result is an *upper bound*, never a
realistic estimate - benchmark with realistic rates before believing a P&L.

## 5. Performance metrics and their assumptions

`StockAnalysis` (`broker/stock.py`) computes annualised return, volatility,
Sharpe ratio, and max drawdown.

- Sharpe, W. F. (1994). "The Sharpe Ratio." *Journal of Portfolio Management*
  21(1):49-58. The canonical definition.
- Lo, A. W. (2002). "The Statistics of Sharpe Ratios." *Financial Analysts
  Journal* 58(4):36-52.
  [doi:10.2469/faj.v58.n4.2453](https://www.tandfonline.com/doi/abs/10.2469/faj.v58.n4.2453).
  Two caveats that apply directly to the code: (a) the `sqrt(window)`
  annualisation in `_calculate_volatility` / `_calculate_sharpe_ratio` assumes
  returns are independent and identically distributed; serial correlation (very
  common in strategy returns) biases the annualised Sharpe, sometimes badly.
  (b) A Sharpe ratio is an *estimate* with its own standard error - two
  strategies whose Sharpes differ by a little are often statistically
  indistinguishable.

Also note `_calculate_sharpe_ratio` uses a zero risk-free rate (it divides mean
return by its standard deviation with no `rf` subtracted). That is a
simplification, defensible at current scale but worth a comment so it is not
mistaken for a true excess-return Sharpe.

Max drawdown is a legitimate, intuitive risk measure but is highly sample- and
horizon-dependent; treat it as descriptive, not as a number to optimise directly.

## 6. Methodological risks - the actual reality check

This is the part that determines whether traderbot produces knowledge or
self-deception.

**Backtest overfitting / data snooping (the fuzzer).**
`scripts/fuzz-strat.py` generates random strategies, backtests each, and keeps
the best. This is, precisely, the procedure the literature warns about: search
enough configurations and one will look brilliant on past data by chance alone.

- White, H. (2000). "A Reality Check for Data Snooping." *Econometrica*
  68(5):1097-1126.
  [doi:10.1111/1468-0262.00152](https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0262.00152)
  ([free PDF](https://users.ssc.wisc.edu/~bhansen/718/White2000.pdf)). The
  bootstrap test for whether the best rule out of many genuinely beats a
  benchmark.
- Bailey, D. H., Borwein, J. M., Lopez de Prado, M., & Zhu, Q. J. (2014).
  "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest
  Overfitting on Out-of-Sample Performance." *Notices of the AMS* 61(5):458-471.
  [free PDF](https://www.ams.org/notices/201405/rnoti-p458.pdf). Shows how few
  configurations it takes to manufacture an impressive but meaningless backtest.
- Bailey, D. H., & Lopez de Prado, M. (2014). "The Deflated Sharpe Ratio."
  *Journal of Portfolio Management* 40(5):94-107.
  [SSRN 2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551).
  The fix for the fuzzer's metric: deflate the winner's Sharpe by the number of
  trials so selection bias is priced in.
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). "...and the Cross-Section of
  Expected Returns." *Review of Financial Studies* 29(1):5-68.
  [doi:10.1093/rfs/hhv059](https://academic.oup.com/rfs/article/29/1/5/1843824).
  After enough multiple testing, the usual t > 2 significance bar is wrong; the
  hurdle rises (they argue t > 3). The more strategies the fuzzer tries, the
  higher the bar the winner must clear.

Concretely, for `fuzz-strat.py`: it must score on **out-of-sample** data the
search never saw (walk-forward, below), report the **number of trials**, and
judge the winner with a **deflated** metric - otherwise its output is the
expected value of noise. (Separately, the current scorer is incomplete: it calls
`trader.trade()` once and reads `trader.capital`, rather than replaying the
history bar by bar and computing P&L - the two `TODO`s in the file flag this.
The bar-by-bar backtest loop is the prerequisite for any of this to mean
anything.)

**Lookahead bias.** The `traderbot-signal` skill and the no-lookahead safety
invariant exist for this reason: a backtest that lets a signal peek at a future
bar reports returns the live bot can never earn. It is the most common way a
backtest lies. The standard reference for doing backtests without these biases:

- Lopez de Prado, M. (2018). *Advances in Financial Machine Learning.* Wiley.
  ISBN 978-1119482086. (Purged / combinatorial cross-validation, the "why most
  backtests fail" chapter.)

**Walk-forward / out-of-sample validation.** The discipline the project still
needs: fit/select on one window, evaluate on the next unseen window, roll
forward.

- Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies,*
  2nd ed. Wiley. ISBN 978-0470128015. (Walk-forward analysis.)

**Survivorship bias.** `Stock` pulls current tickers from yfinance. A universe
that excludes delisted/bankrupt names inflates backtest returns. If strategy
selection ever ranges over multiple symbols, the universe must include the names
that died.

## 7. Position sizing

The `Trader`'s fixed 10%-of-initial-capital cap is a crude heuristic. The
theory of growth-optimal sizing:

- Kelly, J. L. (1956). "A New Interpretation of Information Rate." *Bell System
  Technical Journal* 35(4):917-926.
  [doi:10.1002/j.1538-7305.1956.tb03809.x](https://onlinelibrary.wiley.com/doi/abs/10.1002/j.1538-7305.1956.tb03809.x)
  ([PDF](https://www.princeton.edu/~wbialek/rome/refs/kelly_56.pdf)).

Kelly (and fractional-Kelly, which practitioners use because full Kelly is
brutally volatile) sizes bets by edge and odds rather than a flat fraction. This
is the literature `proposals/position-sizing.md` should reference when it makes
sizing pluggable - but Kelly needs an estimate of edge, and per Sections 1-2 and
6 that estimate is the hard part, so a conservative fixed fraction is a
reasonable default until the edge estimation is trustworthy.

## 8. A note on the ensemble (`DefaultStrategy`)

Majority-voting several indicators borrows the intuition of ensemble methods -
combine weak learners into a stronger one. The caveat specific to this codebase:
the indicators are all deterministic functions of the *same* `Close` series, so
their signals are highly correlated. Ensemble theory's variance-reduction
benefit assumes the components make *partially independent* errors; correlated
components add far less than their count suggests. A five-indicator vote is not
five independent opinions. If diversification of signal is the goal, indicators
drawing on genuinely different information (price vs. volume vs. cross-sectional)
help more than five price-derived oscillators.

## How to cite in this repo

When you add or modify a technique, follow the `CONTRIBUTING.md` "Cite the
source you implement or diverge from" rule, and prefer the tiers in that order:

1. **Primary literature** (this file): the paper or book that introduced or
   rigorously tested the method. This is the grounding.
2. **Practitioner explainers** (Investopedia, alpharithms, StockCharts, already
   in the indicator docstrings): fine as a "how to compute it" pointer, clearly
   secondary, never the sole justification that a method works.

If a technique has no primary source - some classical TA does not - say so
plainly, as Section 2 does for the Stochastic Oscillator. An honest "this is
practitioner folklore with weak empirical support" is more useful than a
tutorial link dressed up as evidence.
