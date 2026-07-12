# AGENT.md — правила агентной разработки для Options Desk

Этот файл — основной контракт для AI-агентов, которые работают с репозиторием `options-desk`.

## Язык общения

- С пользователем отвечать **по-русски**.
- Код, имена переменных, commit messages, PR titles и технические идентификаторы можно писать по-английски, если это естественно для проекта.
- Если пользователь явно просит другой язык — следовать явной просьбе.

## Что это за проект

Options Desk — статическое React/TypeScript приложение для просмотра опционных цепочек.

Ключевые части:

- `src/main.tsx` — основное React-приложение, провайдеры данных, state/cache, UI.
- `src/index.css` — Tailwind CSS v4, theme tokens, sticky desk/grid CSS.
- `scripts/fetch_data.py` — build-time static cache generator: yfinance + Cboe greeks enrichment + `data/index.json`.
- `scripts/yahoo-proxy.ts` — локальный Bun proxy для Yahoo/NASDAQ/CBOE/search.
- `scripts/cloudflare-worker.js` — Cloudflare Worker proxy для публичного GitHub Pages.
- `data/*.json` — статический cache опционных цепочек.
- `data/index.json` — manifest: `files`, `count`, `generated`, `names`, `no_options`.

## Текущая архитектура данных

### Провайдеры

- `marketdata.app` — direct browser, AAPL без ключа, остальные тикеры с token.
- `Static cache` — читает `data/*.json` same-origin.
- `DoltHub` — исторический архив `2024-11-11`, не live.
- `Yahoo via proxy` — lazy provider через `/api/options`.
- `NASDAQ via proxy` — bulk provider через `/api/nasdaq`.
- `CBOE via proxy` — bulk provider через `/api/cboe`.

### Greeks

Статический cache после refresh может содержать:

- per-quote: `delta`, `gamma`, `theta`, `vega`;
- per-quote metadata: `greeksSource`, `greeksMissingReason`;
- top-level metadata: `greeks` summary.

Правила:

- `greeksSource: "cboe"` — provider-supplied Cboe delayed greeks.
- `greeksSource: "black-scholes"` — модельная оценка, не provider data.
- `greeksSource: null` + `greeksMissingReason` — greeks не удалось получить/посчитать.
- Значение `0.0` — это реальное значение/округление до нуля, не missing.
- Missing data в desk UI показывается пустой ячейкой, а не dash.

## Методология работы агента: Spec → Verifier → Environment

Перед существенными изменениями агент должен пройти три этапа.

### 1. The Spec

- Сначала понять бизнес-цель, а не только поверхностную задачу.
- Если задача неоднозначна — интервьюировать пользователя, задавая конкретные вопросы.
- Разбивать работу на небольшие изолированные buckets.
- Для архитектурных развилок просить подтверждение пользователя.

### 2. The Verifier

До кодинга определить, чем будет проверяться результат:

- `npm run build` — основной frontend build.
- `python -m py_compile scripts/fetch_data.py` — синтаксис Python fetcher.
- `node --check scripts/cloudflare-worker.js` — синтаксис Worker.
- Для изменений в data fetcher — локальный точечный smoke test на одном тикере, если это безопасно.
- Для UI изменений — build минимум; если возможно, дополнительно ручной сценарий описать в PR.

### 3. The Environment

Работать через git branch + PR.

- Всегда начинать с актуального `origin/master`, если пользователь просит новую задачу.
- Не смешивать data-refresh commits с UI/docs изменениями, если пользователь не попросил.
- Не коммитить `dist/`, `node_modules/`, `.parcel-cache`, `package-lock.json`, `.venv`, `__pycache__`.
- Учитывать, что предоставленный PAT может не иметь `workflow` scope; workflow-файлы менять только если push разрешён или пользователь дал подходящий token.

## Автопилот / спросить сначала / никогда

### Автопилот

Можно делать без отдельного подтверждения, если задача уже согласована:

- исправлять stale comments/docs в затронутых файлах;
- запускать build/lint/smoke checks;
- создавать feature branch;
- пушить branch и создавать PR;
- добавлять type-safe metadata, если она нужна для уже согласованной функциональности;
- править README/agent docs, чтобы они соответствовали фактическому коду.

### Спросить сначала

Нужно спросить перед тем как:

- менять схему `data/*.json` так, что старые файлы перестанут читаться;
- массово перегенерировать/коммитить `data/*.json`;
- менять `.github/workflows/*`;
- менять provider ordering или default provider;
- добавлять платный API/provider;
- удалять крупные исторические changelog sections;
- менять UX по умолчанию, если это не явно задано пользователем.

### Никогда не делать

- Не раскрывать secrets/tokens в коммитах, README, PR body или логах.
- Не коммитить локальные build/cache artifacts.
- Не делать force push в чужие ветки без явной команды.
- Не менять workflow-файлы, если token не имеет `workflow` scope и push будет заблокирован.
- Не утверждать, что provider data гарантированно 100% complete, если источник free/delayed/best-effort.
- **НИКОГДА не искать/перебирать/grep-ить/listaть файлы в `data/` директории.** Там ~4000 файлов (тикеров). Это займёт очень много времени. Допустимые случаи:
  - Если известен конкретный тикер (например, AAPL) — можно прочитать `data/AAPL.json` напрямую.
  - Если нужно проверить существование файла или прочитать `data/index.json` для общего обзора.
  - Если задача явно требует работу с конкретным тикером/файлом.
  - ВСЕ остальные случаи — сначала спросить пользователя.

## Комментарии и agentic headers

- Сохранять полезные архитектурные комментарии.
- Исправлять или удалять stale comments, если они вводят в заблуждение.
- Agentic changelog должен отражать реальное поведение.
- Не добавлять комментарии “на всякий случай”, если они не помогают будущему агенту.

## PR checklist

Перед PR:

```bash
npm run build
python -m py_compile scripts/fetch_data.py
node --check scripts/cloudflare-worker.js
git diff --check
```

Если менялись только docs — build всё равно желателен, если затронуты source comments рядом с кодом.

В PR body указать:

- что изменено;
- как проверено;
- есть ли ограничения/следующие шаги;
- если data files не обновлялись — явно написать это.
