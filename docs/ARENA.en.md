# ARENA.en.md — adapter for Arena.ai Agent Mode

> **Languages:** English (current) · [Русский](ARENA.ru.md) · **Main contract:** [`AGENT.md`](../AGENT.md).

This file contains specific instructions for Arena.ai Agent Mode.

## Required behavior
- Respond to the user in the language they use or follow the project language rule.
- Use the **Spec → Verifier → Environment** methodology.
- For JS/TS work use only **Bun** (not npm).
- For Python work use **uv**.

## Development commands
When testing local changes use:
```bash
bun run stop ; bun run kill ; bun run ps ; bun run start ; sleep 3 ; bun run logs
```

## Data testing
For updates of specific tickers:
```bash
TICKERS=PEP,KO MAX_FETCHES=3 NASDAQ_TIMEOUT=5 uv run --with yfinance --with requests python scripts/fetch_data.py
```

## Developer Guide
Details in [DEVELOPMENT.en.md](./DEVELOPMENT.en.md) / [DEVELOPMENT.ru.md](./DEVELOPMENT.ru.md).
