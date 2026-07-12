# CLAUDE.md — инструкции для Claude Code / Claude-совместимых агентов

> Главный источник правил для всех агентов: [`AGENT.md`](./AGENT.md). Этот файл — адаптер для Claude Code и похожих инструментов.

## Обязательное поведение

- Отвечай пользователю по-русски.
- Перед кодингом для неоднозначных задач применяй цикл **Spec → Verifier → Environment** из `AGENT.md`.
- Не принимай поверхностную формулировку задачи, если не хватает бизнес-контекста.
- Для крупных архитектурных решений задавай вопросы и жди checkpoint.
- После изменений запускай релевантные проверки и указывай их в PR.

## Проектный контекст

Options Desk — static options-chain desk:

- Frontend: React + TypeScript + Tailwind CSS v4.
- Build: Bun scripts + Parcel.
- Providers (UI labels): **CACHE**, **CBOE**, **NASDAQ**, **YAHOO** only.
- Dropdown order always: CACHE, CBOE, NASDAQ, YAHOO. Default only: localhost → CBOE; Pages → CACHE.
- Static cache: `data/*.json` + `data/index.json`.
- Data fetcher: `scripts/fetch_data.py`.
- Proxy infra: `scripts/yahoo-proxy.ts`, `scripts/cloudflare-worker.js`.

Не путать:

- `CBOE` provider — live/delayed через proxy.
- `CACHE` — same-origin static JSON (build-time Cboe **1st-order** only; BS in UI).
- `black-scholes` greeks — model estimate **только в UI** (`src/main.tsx`); не дублировать в `fetch_data.py`.
- `marketdata` / `DoltHub` больше не в registry.

## Проверки

Минимальный набор:

```bash
npm run build
python -m py_compile scripts/fetch_data.py
node --check scripts/cloudflare-worker.js
git diff --check
```

Если меняется `scripts/fetch_data.py`, по возможности сделать smoke test с одним тикером и не коммитить массовый data refresh без явного запроса.

## Работа с файлами

- Основная логика UI — `src/main.tsx`.
- Стили desk/grid/sticky — `src/index.css`.
- Agent docs — `AGENT.md`, `CLAUDE.md`, `AGENTS.md`, `Setup.md`.
- Не коммитить `dist/`, `node_modules/`, `.parcel-cache`, `.venv`, `__pycache__`, `package-lock.json`.

## Важное про `CLAUDE.md`

Claude Code обычно читает `CLAUDE.md` автоматически, когда работает в репозитории. Но не все agent runners делают это одинаково.

Для Arena.ai Agent Mode нельзя полагаться на 100% auto-load этого файла в каждом новом диалоге. Если задача критична, лучше явно сказать агенту: “прочитай AGENT.md / CLAUDE.md перед началом”.
