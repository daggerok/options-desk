# CLAUDE.md — Адаптер для Claude Code

> **Основной контракт:** [`AGENT.md`](../AGENT.md).

## Обязательное поведение
- По умолчанию отвечайте пользователю на **английском**.
- Используйте методологию **Spec → Verifier → Environment**.
- Используйте **Bun** для JS/TS и **uv** для Python.

## Верификация
```bash
bun run build
uv run python -m py_compile scripts/fetch_data.py
node --check scripts/cloudflare-worker.js
git diff --check
```
