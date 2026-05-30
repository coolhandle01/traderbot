# traderbot - AI Contributor Guide

**Read `CONTRIBUTING.md` first.** It carries the universal rules (ASCII only,
minimal diff, cite-your-source, suppressions-carry-a-reason, FIXME/TODO grammar,
preserve names, surface concerns), the `Before you commit` CI stack, the test
discipline, and the trading **safety invariants** (no lookahead, HOLD on
insufficient data, fee-clearing, the sell gate, the sizing cap, ledger balance,
the deep-copy invariant). Everything below is AI-contributor-specific on top.

## Before you start work

The contributor skills below auto-load on the first matching edit - which is too
late, because by then you have already chosen an approach. Read the relevant
skill while you are still scoping the change, so the conventions are in your head
before you write. You can load any skill on demand with the `Skill` tool (for
example `traderbot-signal`).

Then ask what canonical knowledge the change will produce that is not yet in a
skill, and update the skill in the same change - so what follows is the skill
being applied, not rediscovered after the fact.

## Commit messages

Never include private session URLs (`https://claude.ai/code/session_...`) in
commit messages or PR bodies. Keep them out of anything pushed to the repo.

## Skills

Contributor skills under `.claude/skills/` auto-load via a `PreToolUse` hook on
`Write` / `Edit`, configured in `.claude/settings.json`. On the first edit that
matches a skill's path patterns, that skill's full `SKILL.md` is injected into
context, deduplicated per session so repeated edits to the same area are silent.

| Skill | Triggers on | Carries |
|---|---|---|
| `traderbot-signal` | `trader/indicators/*.py`, `trader/strategy.py`, `trader/strategies/*.py` | the shared `signal(df) -> Signal` contract: no lookahead, HOLD on insufficient data, integer `Signal` for vote-summing, no I/O |
| `traderbot-indicator` | `trader/indicators/*.py` | the `Indicator` ABC, window params, pandas compute, the in-place-column convention and the isolation proposal, `Report` coupling |
| `traderbot-strategy` | `trader/strategy.py`, `trader/strategies/*.py` | aggregation (majority vote), the `configure()` fee-context hook, fee-aware thresholds |
| `traderbot-trader` | `trader/trader.py`, `trader/state.py` | position sizing (10% cap), the fee/tax-netted sell gate, the `TraderState` machine, buy/sell guards |
| `traderbot-broker` | `broker/broker.py`, `broker/ledger.py`, `broker/position.py`, `examples/brokers/*.py` | the `Broker` ABC contract, the double-entry ledger invariant, the mock-vs-live split |
| `traderbot-data` | `broker/stock.py` | yfinance cache, the deep-copy invariant, point-in-time history |
| `traderbot-tests` | `tests/*.py` | the synthetic-OHLCV fixture pattern, no-I/O `Stock`, the `_Fixed` stub, force-the-branch discipline |

The stack is generic-first: `traderbot-signal` is the universal `signal(df)`
contract shared by every indicator and strategy, and the layer specialist
(`traderbot-indicator` or `traderbot-strategy`) loads on top so it lands more
prominently in context. Where a path matches both, you see the contract first
and the specialist last.

The hook has an `in_tests` pre-classifier: `*` crosses `/` in bash `case`
patterns, so without it a future `tests/trader/` mirror dir would over-match the
trader-side patterns and pull author skills into test edits. Edits under
`tests/` load `traderbot-tests` only.

The matching logic lives in `.claude/hooks/load-skill.sh`; it is wired in
`.claude/settings.json`. The hook is defensive - it noops silently if `jq` is
missing or the input shape is unexpected, and never blocks an edit. If a hook
does not fire in your session, run `/hooks` once (or restart) - the watcher only
sees `.claude/settings.json` if it existed at session start. You can always load
a skill manually with the `Skill` tool.

## Design proposals

`proposals/` holds in-flight design docs. Before reworking an area one covers -
indicator isolation / thread-safety, strategy position-sizing, strategy
serialisation, the Trading 212 order API - read the proposal and either follow
it or update it in the same change rather than landing a conflicting partial
version.
