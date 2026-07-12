# CLAUDE.md — Adapter for Claude Code

> **Main Contract:** [`AGENT.md`](./AGENT.md).

## Required Behavior
- Respond to the user in **English** by default.
- Follow **Spec → Verifier → Environment** methodology.
- Use **Bun** for JS/TS and **uv** for Python.

## Verification
```bash
bun run build
uv run python -m py_compile scripts/fetch_data.py
node --check scripts/cloudflare-worker.js
git diff --check
```
