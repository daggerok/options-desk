# ARENA.md — Adapter for Arena.ai Agent Mode

> **Main Contract:** [`AGENT.md`](./AGENT.md).

## Required Behavior
- Respond to the user in **English** by default.
- Follow **Spec → Verifier → Environment** methodology.
- Use **Bun** for JS/TS and **uv** for Python.

## Dev Commands
```bash
bun run stop ; bun run kill ; bun run ps ; bun run start ; sleep 3 ; bun run logs
```

## Data Testing
```bash
TICKERS=PEP,KO MAX_FETCHES=3 NASDAQ_TIMEOUT=5 uv run --with yfinance --with requests python scripts/fetch_data.py
```
