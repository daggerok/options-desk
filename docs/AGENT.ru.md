# AGENT.md — Правила агентной разработки для Options Desk

Этот файл является основным контракте для AI-агентов, работающих с репозиторием `options-desk`.

## Язык общения
- По умолчанию отвечайте пользователю на **английском**.
- Используйте русский язык, если пользователь явно об этом просит или если контекст проекта этого требует.
- Код, имена переменных, сообщения коммитов, названия PR и технические идентификаторы должны быть на английском языке.

## Что это за проект
Options Desk — статическое приложение на React/TypeScript для просмотра опционных цепочек (GitHub Pages + localhost).

Ключевые части:
- `src/main.tsx` — React приложение: **4 провайдера**, состояние/кэш, UI, **только** Black-Scholes / греки высших порядков.
- `src/index.css` — Tailwind CSS v4, токены тем, CSS для закрепленной доски/сетки.
- `scripts/fetch_data.py` — генератор кэша (CACHE) при сборке: yfinance + **Cboe delayed 1st-order only** + `data/index.json`. **Без** модели BS.
- `scripts/yahoo-proxy.ts` — локальный прокси на Bun: `/api/cboe`, `/api/nasdaq`, `/api/options` (Yahoo), `/api/search`.
- `scripts/cloudflare-worker.js` — Cloudflare Worker с теми же эндпоинтами (+ `/raw`).
- `data/*.json` — статический кэш цепочек (котировки + опциональные греки Cboe 1-го порядка).
- `data/index.json` — манифест: `files`, `count`, `generated`, `names`, `no_options`.

Документация для агентов:
- `AGENT.md` — этот файл (основной контракт).
- `CLAUDE.md` — адаптер для Claude Code.
- `ARENA.md` — конфигурация для Arena.ai Agent Mode.
- `AGENTS.md` — заглушка для совместимости.
- `docs/Setup.md` — руководство по агентной настройке.
- `docs/DEVELOPMENT.md` — руководство разработчика.

## Архитектура данных

### Провайдеры (всего 4)
Короткие метки в **верхнем регистре** в UI. Порядок в выпадающем списке **фиксирован везде**:
`CACHE, CBOE, NASDAQ, YAHOO`

- Выбор по умолчанию: `cboe` на localhost/LAN, `static` на хостинге.
- Порядок никогда не меняется в зависимости от хоста.

### Греки — единый источник истины (без дублирования)
- `scripts/fetch_data.py`: yfinance + только **1-й порядок** Cboe. Без BS.
- `src/main.tsx`: Полная модель Black-Scholes + греки высших порядков.

## Методология: Spec → Verifier → Environment

### 1. Spec (Спецификация)
- Понять бизнес-цель.
- Задавать уточняющие вопросы.
- Разделять работу на небольшие изолированные этапы.

### 2. Verifier (Верификация)
```bash
bun run build
uv run python -m py_compile scripts/fetch_data.py
node --check scripts/cloudflare-worker.js
git diff --check
```
- **Локальная разработка/тест:** `bun run stop ; bun run kill ; bun run ps ; bun run start ; sleep 3 ; bun run logs`
- **Smoke тест загрузчика данных:** `TICKERS=PEP,KO MAX_FETCHES=3 NASDAQ_TIMEOUT=5 uv run --with yfinance --with requests python scripts/fetch_data.py`

### 3. Environment (Окружение)
- Используйте **Bun** (JS/TS) и **uv** (Python).
- Работайте в ветках фич + PR.
- Не коммитьте сгенерированные артефакты.

## PR Checklist
- Код имеет ограниченный объем.
- Тесты сборки/линтера/smoke проходят.
- Документация обновлена (включая i18n).
- Секреты отсутствуют.
