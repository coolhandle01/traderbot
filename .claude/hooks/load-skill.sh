#!/usr/bin/env bash
#
# Claude Code PreToolUse hook for Write|Edit.
#
# Maps the target file path to a stack of traderbot contributor skills and
# injects each matched skill's SKILL.md into the model context via
# hookSpecificOutput.additionalContext - auto-loading the relevant skills
# before each edit.
#
# Stacking: a path may match more than one skill. Every Indicator and Strategy
# shares the signal(df) -> Signal contract, so trader/indicators/*.py,
# trader/strategy.py and trader/strategies/*.py all match the generic
# traderbot-signal skill first; the layer specialist (traderbot-indicator or
# traderbot-strategy) then stacks on top, so the specialist appears later in
# the context window.
#
# Session-scoped sentinel: each skill is injected at most once per session, on
# the first matching Edit/Write. Subsequent edits in the same session are
# silent for skills that have already loaded.
#
# Wired via .claude/settings.json. Silently noops if jq is missing or the
# expected stdin shape is absent - never blocks the edit.
#
set -uo pipefail

# Bail quietly on anything unexpected - this hook must never break a tool call.
trap 'exit 0' ERR

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
session_id=$(echo "$input" | jq -r '.session_id // ""')

[ -z "$file_path" ] && exit 0
[ -z "$session_id" ] && exit 0

# Repo-root anchor: hook runs from project cwd; resolve skill paths against it.
repo_root=$(cd "$(dirname "$0")/../.." && pwd)
skills_root="$repo_root/.claude/skills"
state_dir="${TMPDIR:-/tmp}/traderbot-skills-$session_id"
mkdir -p "$state_dir"

# Build the matched-skill stack. Generic matchers come first; specialists
# layer on top. Each branch is independent so a path can match more than one.
matches=()

# Pre-classify: paths under tests/ get the tests skill, never the author-side
# ones. `*` crosses `/` in case patterns, so a future tests/trader/ mirror dir
# would otherwise over-match the trader-side patterns and pull author skills
# into test edits where the test-author guidance applies instead.
case "$file_path" in
    */tests/*) in_tests=1 ;;
    *)         in_tests=0 ;;
esac

if [ "$in_tests" = 0 ]; then
    # traderbot-signal is the generic signal(df) -> Signal contract shared by
    # every Indicator and every Strategy: decide only from the latest bar (no
    # lookahead), HOLD on insufficient data, never raise, no I/O. Matched
    # first so each specialist stacks on top.
    case "$file_path" in
        */trader/indicators/*.py|*/trader/strategy.py|*/trader/strategies/*.py)
            matches+=(traderbot-signal)
            ;;
    esac

    # Indicator specialist - the Indicator ABC, window params, the in-place
    # DataFrame convention and column-naming.
    case "$file_path" in
        */trader/indicators/*.py)
            matches+=(traderbot-indicator)
            ;;
    esac

    # Strategy specialist - aggregation, the configure() fee-context hook,
    # fee-aware thresholds.
    case "$file_path" in
        */trader/strategy.py|*/trader/strategies/*.py)
            matches+=(traderbot-strategy)
            ;;
    esac

    # Trader engine - position sizing, the fee/tax-netted sell gate, the
    # TraderState machine, buy/sell guards.
    case "$file_path" in
        */trader/trader.py|*/trader/state.py)
            matches+=(traderbot-trader)
            ;;
    esac

    # Broker execution + ledger - the Broker ABC contract, the double-entry
    # receipt invariant, the mock-vs-live split. Live adapters live under
    # examples/ (outside the mypy gate) and share the same contract.
    case "$file_path" in
        */broker/broker.py \
        |*/broker/ledger.py \
        |*/broker/position.py \
        |*/broker/__init__.py \
        |*/examples/brokers/*.py)
            matches+=(traderbot-broker)
            ;;
    esac

    # Data layer - yfinance cache, the deep-copy invariant on copy()/tail(),
    # point-in-time history.
    case "$file_path" in
        */broker/stock.py)
            matches+=(traderbot-data)
            ;;
    esac
fi

# Tests - the synthetic-OHLCV fixture pattern, deterministic series, the unit
# marker, no network in unit tests.
case "$file_path" in
    */tests/*.py)
        matches+=(traderbot-tests)
        ;;
esac

[ "${#matches[@]}" -eq 0 ] && exit 0

# Emit each matched skill once per session, joined into a single
# additionalContext blob in stack order (generic first, specialist on top).
combined=""
for skill_name in "${matches[@]}"; do
    sentinel="$state_dir/$skill_name"
    [ -f "$sentinel" ] && continue

    skill_path="$skills_root/$skill_name/SKILL.md"
    [ -f "$skill_path" ] || continue

    touch "$sentinel"
    content=$(cat "$skill_path")
    header="Auto-loading skill $skill_name (matched on file path; this is its first edit this session)."
    if [ -n "$combined" ]; then
        combined="$combined"$'\n\n---\n\n'
    fi
    combined="${combined}${header}"$'\n\n'"${content}"
done

[ -z "$combined" ] && exit 0

jq -n --arg content "$combined" '
    {
        hookSpecificOutput: {
            hookEventName: "PreToolUse",
            additionalContext: $content
        }
    }
'

exit 0
