# CLAUDE.md

## Before pushing

Run the full CI check suite locally before every push:

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy broker trader
```

All three must pass cleanly. If `ruff format --check` fails, run `ruff format .` to fix formatting, then re-check. Do not push code that would fail CI.
