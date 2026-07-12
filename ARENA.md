# ARENA.md — адаптер для Arena.ai Agent Mode

> **Главный контракт:** [`AGENT.md`](./AGENT.md).

Этот файл содержит специфичные инструкции для Arena.ai Agent Mode.

## Обязательное поведение
- Всегда отвечай пользователю **по-русски**.
- Используй методологию **Spec → Verifier → Environment**.
- Для работы с JS/TS используй только **Bun** (не npm).
- Для работы с Python используй **uv**.

## Команды разработки
При тестировании локальных изменений используй:
```bash
bun run stop ; bun run kill ; bun run ps ; bun run start ; sleep 3 ; bun run logs
```

## Тестирование данных
Для получения обновлений конкретных тикеров:
```bash
TICKERS=PEP,KO MAX_FETCHES=3 NASDAQ_TIMEOUT=5 uv run --with yfinance --with requests python scripts/fetch_data.py
```

## Developer Guide
Подробности в [DEVELOPMENT.md](./DEVELOPMENT.md).
