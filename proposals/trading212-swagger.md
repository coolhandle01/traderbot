# Proposal: Trading212 Broker from Swagger

## Problem

The handwritten `Trading212` broker in `examples/brokers/trading212.py` cannot actually buy or sell — `buy()` and `sell()` update local variables but never call the API. `capital()` and `position()` ignore the API response and return hardcoded values. It's a stub dressed as an implementation.

## Proposed Approach

Generate the HTTP client from the official Trading212 OpenAPI spec, then write a thin `Broker` adapter on top.

### Step 1 — Generate the client

```bash
pip install openapi-python-client
openapi-python-client generate --url https://t212public-api-docs.redoc.ly/openapi.yaml \
    --output-path examples/brokers/trading212_client
```

This produces a typed, auto-maintained client with a method per endpoint.

### Step 2 — Write the adapter

```python
class Trading212(Broker):
    def __init__(self, api_key: str, mode: str = "live") -> None:
        self._client = AuthenticatedClient(
            base_url=f"https://{mode}.trading212.com",
            token=api_key,
        )

    def capital(self, symbol: str) -> float:
        account = get_account_cash.sync(client=self._client)
        return account.free if account else 0.0

    def position(self, symbol: str) -> float:
        pos = get_portfolio_position.sync(ticker=symbol, client=self._client)
        return pos.quantity if pos else 0.0

    def buy(self, symbol: str, amount: float) -> float:
        order = place_equity_order.sync(client=self._client, body=MarketOrder(...))
        return order.filled_quantity if order else 0.0

    def sell(self, symbol: str, amount: float) -> float:
        order = place_equity_order.sync(client=self._client, body=MarketOrder(...))
        return order.filled_value if order else 0.0
```

### Step 3 — Add the client to `.gitignore` / generate in CI

The generated client should either be committed (stable, reviewable) or regenerated in CI from a pinned spec version. Recommend committing it — it makes diffs visible when the API changes.

## Files Affected

- `examples/brokers/trading212.py` — replace with the adapter above
- `examples/brokers/trading212_client/` — generated client (new)
- `pyproject.toml` — add `openapi-python-client` as a dev dependency
- `.gitignore` — optionally exclude the generated client
- `tests/` — add integration tests against Trading212 paper trading (sandbox)

## Open Questions

- Paper account or live? The adapter should accept `mode="demo"` to target the sandbox.
- The Trading212 API uses fractional shares — does `amount` mean cash value or share count? Need to align with how `Trader` calls `buy(symbol, amount)`.
