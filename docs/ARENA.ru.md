# ARENA.md — Адаптер для Arena.ai Agent Mode

> **Основной контракт:** [`AGENT.md`](../AGENT.md).

Этот файл содержит специфические инструкции для Arena.ai Agent Mode.

## Обязательное поведение
- По умолчанию отвечайте пользователю на **английском**.
- Используйте методологию **Spec → Verifier → Environment**.
- Используйте **Bun** для JS/TS и **uv** для Python.

## Команды разработки
```bash
bun run stop ; bun run kill ; bun run ps ; bun run start ; sleep 3 ; bun run logs
```

## Тестирование данных
```bash
TICKERS=PEP,KO MAX_FETCHES=3 NASDAQ_TIMEOUT=5 uv run --with yfinance --with requests python scripts/fetch_data.py
```
