# Contributing to traderbot

This file is the contributor surface: how to run the checks, the rules every
change follows, and the trading-specific safety invariants that hold across the
codebase. If you are working with Claude Code, also read `CLAUDE.md` for the
AI-contributor instructions and the skill catalogue. For project setup and a
runnable example, see `README.md` and `example.py`.

## Before you commit

Run the full CI suite locally before every push. All of it must pass cleanly -
never "push and let CI tell me":

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy broker trader
pytest -m unit --cov --cov-report=term-missing
bandit -c pyproject.toml -r . -q
```

If `ruff format --check` fails, run `ruff format .` to fix it. Note the type
check is scoped to `mypy broker trader` on purpose - `examples/` (the live
broker adapters) and `scripts/` are intentionally outside the typed gate. Do not
drag them under it without committing to maintain their types.

Never push a change you have not actually run. A green `mypy` after removing a
`# type: ignore` means nothing if the file was not reachable.

Read the actual file before planning any change, and check `proposals/` for
in-flight design work that may already cover what you are about to build.

## Universal rules

These apply to every edit.

### ASCII only

All source, comments, docstrings, and Markdown prose stay plain ASCII. No em
dashes, en dashes, curly quotes, arrows, or emoji. Use `-` not an em dash, `->`
not the Unicode arrow, `|` not the Unicode pipe. Unicode punctuation fragments
into extra tokens under byte-level BPE tokenisers, inflating the context cost of
every AI tool that reads this repo; high-frequency ASCII is typically one token.
The direction of the effect is consistent even though the exact ratio is
tokeniser-dependent.

### Minimal diff

One change does one thing. Before committing, run `git diff --stat` and ask
whether every touched file relates to the stated task; if not, revert it or move
it to its own branch. Leave whitespace, import order, and formatting alone unless
the linter required the change. Do not rewrite working code to a "cleaner" form
unless cleanliness was the task.

### Cite the source you implement or diverge from

The indicators already do this - each module docstring links the reference it
implements (Investopedia, alpharithms, StockCharts). Keep the habit, but prefer
the primary source over a tutorial blog: a new indicator, metric, or strategy
names the paper or book it is based on, with the practitioner explainer as a
clearly-secondary "how to compute it" pointer. `docs/academic-grounding.md` is
the register of primary sources for the techniques already in the repo (and an
honest account of what the evidence says about each); add to it when you add a
technique. When you deliberately depart from a standard formula or an upstream
convention, say so in the same place and link what you diverge from, so a future
reader can recover the reasoning instead of assuming a bug.

### Suppressions carry a reason

The codebase already practices this: `# noqa: B027` on the intentionally-empty
`Strategy.configure()` base, `# type: ignore[no-any-return]` on
`Stock.copy()` / `tail()`. A linter, mypy, or bandit finding is the tool
flagging an assumption it could not verify - read it, decide why the code is
actually safe, and prefer making the assumption explicit over silencing it. If
you must suppress, the suppression carries a one-line reason and the specific
code (`# type: ignore[no-any-return]`, not a bare `# type: ignore`; `# noqa:
B027`, not a bare `# noqa`). When you meet an existing suppression, its reason is
the original author handing you context the tool could not encode - read it
before changing what it guards.

### FIXME and TODO grammar

Keep these greppable and actionable. The codebase already uses TODOs that link
the thing to do (`# TODO: implement via Trading 212 order API`, with the API URL
nearby):

```python
# FIXME: Report reads df["%RSI"] but rsi.py writes df["RSI%"] - column mismatch
# TODO: score the strategy on the back-test result (P&L, Sharpe) - see proposals/
```

`FIXME` means wrong or incomplete in a way that should be fixed; `TODO` means
fine but improvable later. Include enough context to act without scrolling git
history. If you cannot phrase it clearly, ask rather than note it.

### Preserve names, comments, and structure unless that is the task

Symbol names, comment wording, and file layout encode the author's intent. Do
not rename, reword, or move code in a PR whose job is something else - it breaks
`git blame`, loses framing, and makes the diff argue two things at once. Before
deleting something that looks redundant, find out why it is there (the safety
invariants below are the documented examples).

### Surface concerns, do not silently override

When you want to break a stated rule - rename for clarity in a non-rename change,
suppress a finding you do not understand, weaken an invariant - stop and, in
order of preference: ask (a one-line question is cheap), or note it as a
FIXME/TODO and proceed with the original task untouched, or defer it to a
follow-up.

## Test discipline

traderbot tests are pure unit tests under the `unit` marker (`pytest -m unit`):
no network, no files, no real broker. Build OHLCV frames by hand, choose price
series that *force* the branch under test (and comment why), and cover the BUY,
SELL, HOLD, and insufficient-data cases for any signal producer. Use `MockBroker`
and a hand-built `Stock` (via `object.__new__`) to stay offline. Compare computed
float money with a `1e-9` tolerance, never `==`. A bug fix lands with a
regression test; a new behaviour lands with coverage of the branches it adds.

## Proposals

Larger design changes start as a short Markdown doc in `proposals/` before the
code lands (`indicator-isolation`, `position-sizing`, `strategy-serialisation`,
`trading212-swagger` are the current set). If your change touches an area a
proposal already covers, follow the proposal or update it in the same change -
do not implement a conflicting partial version ad hoc.

## Safety invariants - do not weaken

These exist for reasons not obvious from a single line of code. Touching any of
them is a deliberate, explained change, not a drive-by.

- **No lookahead.** A `signal(df) -> Signal` decides only from the latest bar(s)
  (`df.iloc[-1]`, `.iloc[-2]` for a crossover). Never index a future row
  (`.iloc[i+1]`, `.shift(-1)`) or compare an interior bar to a future-inclusive
  aggregate. Trailing `rolling` / `ewm` are safe; how you index their result is
  where lookahead sneaks in. Lookahead inflates backtests and is invisible until
  live.
- **HOLD on insufficient data.** `signal()` returns `Signal.HOLD` on short
  history or a NaN result; it never raises and never acts on a NaN comparison.
- **Signal is `-1 / 0 / 1`.** The integer values drive `DefaultStrategy`'s
  vote-summing; do not reorder or stringify them.
- **Strategies clear costs.** A fee-aware strategy reads the round-trip cost in
  `configure(broker, symbol)` and refuses signals that cannot beat it.
- **The Trader sell gate.** `Trader.sell()` only fires when `net > trade_min_profit`,
  with `net` subtracting both the fee rate and stamp-duty rate from gross.
- **Position-sizing cap.** `trade_max_bet` is 10% of *initial* capital; the bot
  never goes all-in on one signal. Changing the base or fraction is a risk-policy
  change.
- **Ledger receipts balance.** Every `Receipt` satisfies `sum(debit) ==
  sum(credit)` (`balanced()`); brokers record through `_record_buy` /
  `_record_sell`, never by hand. Add a cost to both receipt builders or neither.
- **Stock.copy() / tail() deep-copy.** Indicators mutate the frame in place, so
  the data layer hands out deep copies to protect the cached history. Do not
  weaken to a shallow copy or a direct return.
- **Live orders gate on mode.** Anything that places a real Trading 212 order
  defaults to the safe path and requires an explicit live opt-in.

## Pull requests

If you open a PR, make sure you are subscribed to it so review comments and CI
events reach you. Keep the diff scoped to one thing (see Minimal diff).
