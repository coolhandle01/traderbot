# CLAUDE.md

## Before pushing

Run the full CI check suite locally before every push:

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy broker trader
pytest -m unit --cov --cov-report=term-missing
bandit -c pyproject.toml -r . -q
```

All checks must pass cleanly. If `ruff format --check` fails, run `ruff format .` to fix it. Do not push code that would fail CI.

> Note: the semgrep SAST step requires `SEMGREP_APP_TOKEN` to be set as a repo secret — it runs in CI only.
