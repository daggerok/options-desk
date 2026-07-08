# Options Desk [![CI](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml/badge.svg)](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml)
A single-page **options board** — enter a ticker, pick an expiration, and view the classic **Calls | Strike | Puts** chain with bid / mid / ask, IV, volume, open interest and (where the source provides them) greeks. Built as a **static** web app: TypeScript + React (`.tsx`) + Tailwind CSS v4, deployable to **GitHub Pages** with no backend.

> **RU:** Одностраничная **опционная доска** — вводишь тикер, выбираешь дату экспирации и смотришь классическую цепочку **Calls | Strike | Puts** с bid / mid / ask, подразумеваемой волатильностью (IV), объёмом, открытым интересом и греками (где источник их отдаёт). Это **статическое** веб-приложение: TypeScript + React (`.tsx`) + Tailwind CSS v4, разворачивается на **GitHub Pages** без бэкенда.

## Table of contents / Оглавление

- [English](#english)
    - [What you get](#what-you-get)
    - [Quick start](#quick-start)
    - [How to use](#how-to-use)
    - [Data providers](#data-providers)
    - [Deploy to GitHub Pages](#deploy-to-github-pages)
    - [Companion infrastructure](#companion-infrastructure)
    - [Project structure](#project-structure)
    - [Privacy & keys](#privacy--keys)
    - [Troubleshooting](#troubleshooting)
- [Русский](#русский)
    - [Что это умеет](#что-это-умеет)
    - [Быстрый старт](#быстрый-старт)
    - [Как пользоваться](#как-пользоваться)
    - [Провайдеры данных](#провайдеры-данных)
    - [Публикация на GitHub Pages](#публикация-на-github-pages)
    - [Вспомогательная инфраструктура](#вспомогательная-инфраструктура)
    - [Структура проекта](#структура-проекта)
    - [Приватность и ключи](#приватность-и-ключи)
    - [Решение проблем](#решение-проблем)

---

# English

## What you get

- **Top bar:** app name **Option Desk** on the left; on the right — the **API provider** dropdown, a **theme switch** (Light / System / Dark), and a **Settings** gear.
- **Deferred, quota-friendly loading:** nothing is fetched on page open. You explicitly:
    1. type a ticker → **Get dates** (loads only the list of expirations + spot),
    2. choose an expiration → **Load** (fetches that expiration's chain).
- **Cancel button:** any in-flight request can be cancelled (to switch provider/ticker without waiting).
- **Multiple data providers** with a "works-first" order, live setup badges (*No setup / Free key / Needs proxy*) and guided onboarding when a key is required.
- **Theme:** Light / Dark / **System** (follows your OS and updates live).
- **ATM highlight**, sticky table header, themed scrollbars, put-call-parity spot estimate when a source omits the underlying price.
- **Everything is stored locally** in your browser (`localStorage`) — provider choice, theme, API keys, last ticker.

## Quick start

You need any static file server (the app is plain `index.html` + `index.css` + `main.tsx`). Two common ways:

**A) Bun + Vite (recommended for development)**
```bash
bun install
bun run dev        # open the printed localhost URL
```

**B) Any static server**
Because `main.tsx` uses `type="module"`, serve the folder over HTTP (not `file://`). For a production build, bundle with Vite/Bun so the `.tsx` is compiled to JS, then host the output.

Add `?debug=true` to the URL to enable verbose console logging.

## How to use

1. **Pick a provider** in the top-bar **API** dropdown. The default (**marketdata.app**) shows **AAPL with no key at all** — the fastest way to see the app working.
2. **Enter a ticker** (e.g. `AAPL`, `TSLA`, `SPY`) and press **Get dates**.
3. **Choose an expiration** from the dropdown and press **Load**.
4. Read the chain: **Calls** on the left, **Strike** in the center, **Puts** on the right. IV is shown as a percentage; the **ATM row** (nearest the spot) is highlighted.
5. Want any ticker beyond AAPL with no keys? Use **DoltHub** (historical, no setup), or run the local proxy and use **Yahoo** / **CBOE** (any live ticker). Or paste a free **marketdata.app** token in **Settings** (gear) for live any-ticker.

## Data providers

Ordered **works-first**. Badges: **No setup** = usable immediately · **Free key** = one free sign-up · **Needs proxy** = requires a relay.

Every provider below is **privacy-friendly**: none require an account with sensitive personal data.

| Provider | Setup | Coverage | Greeks | Notes |
|---|---|---|---|---|
| **marketdata.app** *(default)* | No setup for **AAPL** | Any ticker with a free token | Yes | AAPL keyless; free token = 100 req/day, data delayed ≥24h. |
| **Static cache (data.json)** | No setup | Only cached tickers | If cached | Reads the site's own `./data/*.json` (built by the GitHub Action). 100% CORS-free on Pages, no keys. |
| **DoltHub** | No setup | Many US tickers | Yes | Free SQL-over-HTTP, no key. **Historical archive (frozen 2024-11-11)** — research/backtesting, **not live**. No volume/OI/spot. |
| **Yahoo (via proxy)** | Needs proxy | Any ticker | No | Needs the crumb-handling proxy (local Bun server or Cloudflare Worker). Set the Proxy base URL in Settings. |
| **CBOE** | Needs proxy | All equities + indices | Yes | Richest live no-key data (greeks/IV/OI + spot), but CBOE sends no CORS header → run it through the same proxy (`/api/cboe`). |

**Removed** (each required a brokerage-style account with sensitive sign-up, or a paid/gated plan that made the free tier unusable for options): **Tradier**, **Alpaca**, **Polygon/Massive**, **Alpha Vantage**.

**How to get the free marketdata.app token**
- **marketdata.app** → <https://www.marketdata.app> (no card; AAPL needs no key at all)

The other providers need **no key** — just, for Yahoo/CBOE, a small proxy you run yourself (see below).

## Deploy to GitHub Pages

The simplest **100% free, no-server** setup is the **Static cache** provider:

1. Enable Pages: repo **Settings → Pages** → deploy from your branch.
2. Allow the Action to commit: **Settings → Actions → General → Workflow permissions → Read and write**.
3. Edit the ticker list in `.github/workflows/update-data.yml` (`TICKERS: "AAPL MSFT SPY …"`).
4. The Action runs on a schedule (and on demand), fetches chains with `yfinance`, and commits fresh `data/*.json`.
5. In the app, pick **Static cache** — it reads your own JSON, so there are **no CORS issues and no keys** in the browser.

Want **live** data on the public site? Deploy `scripts/cloudflare-worker.js` (free), put its URL in **Settings → Proxy base URL**, then choose **Yahoo (via proxy)** or **CBOE** — the Worker serves both (`/api/options` and `/api/cboe`).

**Local live data (no deploy):** run `bun run scripts/yahoo-proxy.ts`, keep the default **Proxy base URL** `http://localhost:8787`, and pick **Yahoo** or **CBOE**. CBOE gives the richest no-key chain (greeks/IV/OI + spot) for any equity or index (`SPX`, `VIX`, …).

## Companion infrastructure

These files are **optional** and live outside the 3-file app source:

- `scripts/fetch_data.py` — **smart** `yfinance` → `data/*.json` fetcher. It discovers a market-cap-ranked US universe (NASDAQ screener), **skips files already refreshed today**, fetches top-down until its per-run budget or a rate-limit, and **appends** to the cache (resumable across runs). No hand-maintained ticker list. Tunables: `MAX_FETCHES`, `UNIVERSE_SIZE`, `MAX_EXPIRATIONS`, `REQUEST_SLEEP` (or `TICKERS="AAPL MSFT"` to override).
- `.github/workflows/update-data.yml` — runs the smart fetcher several times each weekday and commits the JSON (each run only does new work).
- `scripts/yahoo-proxy.ts` — local **Bun** proxy serving **both** `/api/options` (Yahoo, crumb/cookie-handled) **and** `/api/cboe` (CBOE relay). Run: `bun run scripts/yahoo-proxy.ts` (default `http://localhost:8787`).
- `scripts/cloudflare-worker.js` — deployable proxy: `/api/options` (Yahoo), `/api/cboe` (CBOE), and `/raw?url=…` (generic CORS passthrough).

## Project structure

```
index.html                      # app shell (loads index.css + main.tsx)
index.css                       # Tailwind v4 + theme tokens + scrollbars
main.tsx                        # the entire app (providers, UI, state)
data/                           # static cache (built by the Action)
  index.json                    #   { tickers: [...] }
  AAPL.json, SPY.json, …        #   one chain per cached ticker
scripts/
  fetch_data.py                 # yfinance → data/*.json
  yahoo-proxy.ts                # local Bun Yahoo proxy
  cloudflare-worker.js          # deployable proxy (Yahoo + /raw)
.github/workflows/update-data.yml   # scheduled data refresh
```

## Privacy & keys

- **All settings and API keys are stored only in your browser's `localStorage`.** Nothing is sent to any server of ours (there is no server). Keys go **directly** from your browser to the chosen data provider.
- On a **shared computer**, remember that keys persist in `localStorage`. Clear them via the browser, or paste an empty value in Settings.
- For a public deployment where you don't want keys in the browser at all, use the **Static cache** (keys live only in GitHub Actions) or a **Cloudflare Worker** (keys live as Worker secrets).

## Troubleshooting

- **"Needs proxy" / CORS errors (CBOE, Yahoo, sometimes DoltHub):** the source doesn't send CORS headers. Switch the CORS proxy in Settings, or route through your own **Cloudflare Worker** (`/raw?url=…`).
- **`Unexpected token '<'`:** a proxy returned an HTML error page instead of JSON. Pick a different proxy/provider.
- **Rate limit reached:** free tiers are capped (e.g. marketdata.app 100/day). Wait, switch provider, or use the Static cache / DoltHub / CBOE.
- **DoltHub data looks old:** it is — DoltHub is a **frozen historical archive** (~2024-11-11). Use it for research, not live quotes.
- **Nothing loads on open:** that's intentional — press **Get dates**, then **Load** (this avoids wasting your rate limit just by opening the page).

---

# Русский

## Что это умеет

- **Верхняя панель:** слева название **Option Desk**; справа — выпадающий список **провайдера API**, **переключатель темы** (светлая / системная / тёмная) и шестерёнка **настроек**.
- **Отложенная загрузка, бережная к лимитам:** при открытии страницы ничего не грузится. Ты явно:
    1. вводишь тикер → **Get dates** (грузит только список экспираций + спот),
    2. выбираешь экспирацию → **Load** (грузит цепочку этой даты).
- **Кнопка Cancel:** любой текущий запрос можно отменить (чтобы сменить провайдера/тикер, не дожидаясь).
- **Несколько провайдеров данных** в порядке «сначала то, что работает», с бейджами настройки (*No setup / Free key / Needs proxy*) и пошаговой карточкой, когда нужен ключ.
- **Тема:** светлая / тёмная / **системная** (следит за ОС и меняется на лету).
- **Подсветка ATM**, «липкая» шапка таблицы, стилизованные скроллбары, оценка спота через put-call parity, если источник не отдаёт цену базового актива.
- **Всё хранится локально** в браузере (`localStorage`) — выбор провайдера, тема, ключи API, последний тикер.

## Быстрый старт

Нужен любой статический сервер (приложение — это `index.html` + `index.css` + `main.tsx`). Два типовых способа:

**A) Bun + Vite (рекомендуется для разработки)**
```bash
bun install
bun run dev        # открой напечатанный localhost-адрес
```

**B) Любой статический сервер**
Так как `main.tsx` использует `type="module"`, раздавай папку по HTTP (не `file://`). Для продакшена собери проект через Vite/Bun (чтобы `.tsx` скомпилировался в JS) и размести результат.

Добавь `?debug=true` в URL, чтобы включить подробные логи в консоли.

## Как пользоваться

1. **Выбери провайдера** в списке **API** на верхней панели. По умолчанию (**marketdata.app**) показывает **AAPL вообще без ключа** — самый быстрый способ увидеть, что всё работает.
2. **Введи тикер** (например, `AAPL`, `TSLA`, `SPY`) и нажми **Get dates**.
3. **Выбери экспирацию** из списка и нажми **Load**.
4. Смотри цепочку: **Calls** слева, **Strike** по центру, **Puts** справа. IV показана в процентах; строка **ATM** (ближайшая к споту) подсвечена.
5. Нужен любой тикер кроме AAPL без ключей? Используй **DoltHub** (историю, без настройки) или запусти локальный прокси и бери **Yahoo** / **CBOE** (любой live-тикер). Либо вставь бесплатный токен **marketdata.app** в **настройках** (шестерёнка) для любого live-тикера.

## Провайдеры данных

Порядок — **сначала то, что работает**. Бейджи: **No setup** = работает сразу · **Free key** = одна бесплатная регистрация · **Needs proxy** = нужен релей.

| Провайдер | Настройка | Покрытие | Греки | Заметки |
|---|---|---|---|---|
| **marketdata.app** *(по умолчанию)* | Без настройки для **AAPL** | Любой тикер с бесплатным токеном | Да | AAPL без ключа; бесплатный токен = 100 запросов/день, данные с задержкой ≥24ч. |
| **Static cache (data.json)** | Без настройки | Только закэшированные тикеры | Если закэшировано | Читает собственные `./data/*.json` (создаёт GitHub Action). 100% без CORS на Pages, без ключей. |
| **DoltHub** | Без настройки | Многие тикеры США | Да | Бесплатный SQL-по-HTTP, без ключа. **Исторический архив (заморожен 2024-11-11)** — для исследований/бэктеста, **не live**. Без объёма/OI/спота. |
| **Yahoo (via proxy)** | Нужен прокси | Любой тикер | Нет | Нужен прокси с обработкой crumb (локальный Bun-сервер или Cloudflare Worker). Укажи Proxy base URL в настройках. |
| **CBOE** | Нужен прокси | Все акции + индексы | Да | Самые богатые live-данные без ключа (греки/IV/OI + спот), но CBOE не отдаёт CORS-заголовок → через тот же прокси (`/api/cboe`). |

**Удалены** (каждый требовал аккаунта брокерского типа с чувствительной регистрацией либо платного/закрытого плана, из-за чего бесплатный доступ к опционам был непригоден): **Tradier**, **Alpaca**, **Polygon/Massive**, **Alpha Vantage**.

**Где взять бесплатный токен marketdata.app**
- **marketdata.app** → <https://www.marketdata.app> (без карты; AAPL вообще без ключа)

Остальным провайдерам **ключ не нужен** — только для Yahoo/CBOE запусти небольшой прокси у себя (см. ниже).

## Публикация на GitHub Pages

Самый простой **бесплатный вариант без сервера** — провайдер **Static cache**:

1. Включи Pages: **Settings → Pages** в репозитории → публикация с твоей ветки.
2. Разреши Action коммитить: **Settings → Actions → General → Workflow permissions → Read and write**.
3. Отредактируй список тикеров в `.github/workflows/update-data.yml` (`TICKERS: "AAPL MSFT SPY …"`).
4. Action запускается по расписанию (и вручную), тянет цепочки через `yfinance` и коммитит свежие `data/*.json`.
5. В приложении выбери **Static cache** — оно читает твой собственный JSON, поэтому **никаких проблем с CORS и ключей** в браузере нет.

Хочешь live-данные Yahoo на публичном сайте? Задеплой `scripts/cloudflare-worker.js` (бесплатно), укажи его URL в **Settings → Proxy base URL** и выбери **Yahoo (via proxy)**.

## Вспомогательная инфраструктура

Эти файлы **необязательные** и лежат вне трёх исходников приложения:

- `scripts/fetch_data.py` — **умный** сборщик `yfinance` → `data/*.json`. Сам находит вселенную тикеров США, отсортированную по капитализации (скринер NASDAQ), **пропускает файлы, уже обновлённые сегодня**, идёт сверху вниз до лимита запуска или рейт-лимита и **дописывает** кэш (возобновляемо между запусками). Список тикеров вручную вести не нужно. Параметры: `MAX_FETCHES`, `UNIVERSE_SIZE`, `MAX_EXPIRATIONS`, `REQUEST_SLEEP` (или `TICKERS="AAPL MSFT"` для ручного списка).
- `.github/workflows/update-data.yml` — запускает умный сборщик несколько раз в будни и коммитит JSON (каждый запуск делает только новую работу).
- `scripts/yahoo-proxy.ts` — локальный прокси на **Bun**, отдаёт **и** `/api/options` (Yahoo, обработка crumb/cookie), **и** `/api/cboe` (релей CBOE). Запуск: `bun run scripts/yahoo-proxy.ts` (по умолчанию `http://localhost:8787`).
- `scripts/cloudflare-worker.js` — прокси для деплоя: `/api/options` (Yahoo), `/api/cboe` (CBOE) и `/raw?url=…` (универсальный проброс с CORS).

## Структура проекта

```
index.html                      # оболочка (подключает index.css + main.tsx)
index.css                       # Tailwind v4 + токены темы + скроллбары
main.tsx                        # всё приложение (провайдеры, UI, состояние)
data/                           # статический кэш (создаёт Action)
  index.json                    #   { tickers: [...] }
  AAPL.json, SPY.json, …        #   по одной цепочке на тикер
scripts/
  fetch_data.py                 # yfinance → data/*.json
  yahoo-proxy.ts                # локальный Bun-прокси Yahoo
  cloudflare-worker.js          # прокси для деплоя (Yahoo + /raw)
.github/workflows/update-data.yml   # обновление данных по расписанию
```

## Приватность и ключи

- **Все настройки и ключи API хранятся только в `localStorage` браузера.** Ничего не отправляется на наши серверы (их нет). Ключи идут **напрямую** из браузера к выбранному провайдеру данных.
- На **общем компьютере** помни, что ключи остаются в `localStorage`. Очисти их через браузер или вставь пустое значение в настройках.
- Если для публичного деплоя не хочешь держать ключи в браузере вообще — используй **Static cache** (ключи живут только в GitHub Actions) или **Cloudflare Worker** (ключи как секреты Worker).

## Решение проблем

- **«Needs proxy» / ошибки CORS (CBOE, Yahoo, иногда DoltHub):** источник не отдаёт CORS-заголовки. Смени CORS-прокси в настройках или проведи запрос через свой **Cloudflare Worker** (`/raw?url=…`).
- **`Unexpected token '<'`:** прокси вернул HTML-страницу ошибки вместо JSON. Выбери другой прокси/провайдера.
- **Достигнут лимит запросов:** у бесплатных тарифов есть ограничения (например, marketdata.app 100/день). Подожди, смени провайдера или используй Static cache / DoltHub / CBOE.
- **Данные DoltHub выглядят старыми:** так и есть — DoltHub это **замороженный исторический архив** (~2024-11-11). Используй для исследований, не для live-котировок.
- **При открытии ничего не грузится:** это специально — нажми **Get dates**, затем **Load** (так лимит не тратится просто от открытия страницы).

---

*Agentic developer note: this README is kept in sync with `main.tsx` / `index.css` — update the provider table and changelog references whenever a provider or feature changes.*

<!-- old:

---

## 🚀 Features & Architecture
TODO

---

## 🛠️ Tech Stack

* **Runtime:** and **Build Tool:** [Bun](https://bun.sh/)
* **Frontend Library:** React (TypeScript: TSX)
* **Styling Framework:** TailwindCSS v4 (Utility-first, fully embedded optimized SVGs)

---

## 📦 Getting Started

### Prerequisites
Ensure you have [Bun](https://bun.sh/) installed locally on your development machine.

### Installation & Local Run

1. Clone the repository and navigate to the root directory:
   ```bash
   git clone https://github.com/daggerok/options-desk.git && cd $_
   ```

2. Install the necessary development dependencies:
   ```bash
   bun install -E
   ```

3. Launch the local Vite development server with Hot Module Replacement (HMR):
   ```bash
   bun serve
   ```

4. Upgrade all ecosystem packages to their latest absolute versions:
   ```bash
   bunx npm-check-updates -u
   ```

## 📖 Production Deployment & Standalone Build

Since the entire system compiles into a self-contained Single Page Application (SPA) without requiring any heavy node
backend or cloud infrastructure, you can generate a static deployment bundle:

```bash
bun run build && bunx serve ./dist
```

The resulting optimized assets will be located inside the `./dist` folder, ready to be served from any static hosting
architecture or local offline workspace.

-->
