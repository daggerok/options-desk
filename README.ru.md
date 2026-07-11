# Options Desk — Русская документация

Одностраничная **опционная доска**: вводишь тикер, получаешь даты экспираций, выбираешь одну или несколько дат и смотришь цепочку **Calls | Strike | Puts** с bid / mid / ask, IV, объёмом, OI и греками там, где источник их отдаёт. Приложение статическое: React + TypeScript + Tailwind CSS v4, сборка Parcel, деплой на GitHub Pages.

---

## Оглавление

- [Что это умеет](#что-это-умеет)
- [Быстрый старт](#быстрый-старт)
- [Как пользоваться](#как-пользоваться)
- [Провайдеры данных](#провайдеры-данных)
- [Подсказки тикеров](#подсказки-тикеров)
- [Greeks в static cache](#greeks-в-static-cache)
- [Публикация на GitHub Pages](#публикация-на-github-pages)
- [Настройка прокси для GitHub Pages](#настройка-прокси-для-github-pages)
- [Вспомогательная инфраструктура](#вспомогательная-инфраструктура)
- [Структура проекта](#структура-проекта)
- [Приватность и ключи](#приватность-и-ключи)
- [Решение проблем](#решение-проблем)

---

## Что это умеет

- **Двухшаговая загрузка без лишних запросов:** при открытии ничего не грузится. Тикер → **Get dates**; экспирации → **Load**.
- **Подсказки тикеров:** поиск по тикеру/названию для всех провайдеров. Локальные подсказки берут названия из `data/index.json`; тикеры из `no_options` помечаются **`(no options)`**.
- **Несколько экспираций:** можно выбрать одну, несколько или все. Цепочки показываются стопкой от ранней к поздней со sticky-заголовками.
- **Удобная доска:** подсветка ATM, sticky Calls/Strike/Puts, greeks-колонки включены по умолчанию, настройки колонок для каждой стороны (Calls/Puts) отдельно, missing data показывается пустой ячейкой, скроллбары в теме, сворачивание/разворачивание, автопрокрутка к текущему страйку после загрузки/разворачивания.
- **Theme UX:** компактная иконка текущей темы с animated dropdown для остальных тем.
- **Бейджи настройки:** No setup / Free key / Needs proxy и подсказки, если нужен токен.
- **Локальное состояние:** провайдер, тема, токены, URL прокси, последний тикер и кэш запросов хранятся только в `localStorage`.

## Быстрый старт

Проект использует **Bun** для установки/скриптов и **Parcel** для сборки React/TypeScript.

```bash
git clone https://github.com/daggerok/options-desk.git
cd options-desk
bun install -E
bun run serve
```

Открой localhost-адрес, который напечатает Parcel. Для подробных логов добавь `?debug=true`.

Продакшен-сборка:

```bash
bun run build
```

Сборка для GitHub Pages с правильным public URL `/options-desk/`:

```bash
bun run build-github-pages
```

## Как пользоваться

1. Выбери провайдера в списке **API**.
2. Введи тикер или название компании. При необходимости выбери подсказку.
3. Нажми **Get dates**, чтобы получить экспирации и спот.
4. Выбери одну или несколько дат, либо **All**.
5. Нажми **Load**, чтобы увидеть цепочку.

На `localhost` / приватной LAN список провайдеров переворачивается, чтобы прокси-провайдеры были первыми. На hosted/static деплое первыми идут провайдеры без настройки.

## Провайдеры данных

Порядок для hosted/static деплоя — **сначала то, что проще запустить**. Бейджи: **No setup** = работает сразу · **Free key** = бесплатный токен · **Needs proxy** = нужен relay/proxy.

| Провайдер | Настройка | Покрытие | Греки | Заметки |
|---|---|---|---|---|
| **marketdata.app** *(по умолчанию на hosted)* | Без настройки для **AAPL** | Любой тикер с бесплатным токеном | Да | AAPL без ключа; токен открывает остальные тикеры в рамках лимитов marketdata.app. |
| **Static cache (data.json)** | Без настройки | Тикеры из `data/*.json` | CBOE/model-enriched по мере refresh | Same-origin JSON из GitHub Actions/yfinance, обогащается CBOE delayed greeks и Black-Scholes fallback metadata. Без CORS и без токена в браузере. |
| **DoltHub** | Без настройки | Многие тикеры США в архиве | Да | Бесплатный SQL-over-HTTP. Исторический архив заморожен на `2024-11-11`; не live. Без объёма/OI/спота. |
| **Yahoo (via proxy)** | Нужен прокси | Yahoo symbol search/option chains | Нет | Локальный Bun-прокси или Cloudflare Worker обрабатывает crumb/cookies. |
| **NASDAQ (via proxy)** | Нужен прокси | NASDAQ option-chain endpoint | Нет | Полная цепочка за один запрос: bid/ask/last/volume/OI. Браузеру нужен прокси. |
| **CBOE (via proxy)** | Нужен прокси | CBOE delayed options endpoint | Да | Богатые delayed-данные с greeks/IV/OI/spot. Браузеру нужен прокси. |

Эксперименты с удалёнными провайдерами оставлены только в истории changelog: Tradier, Alpaca, Polygon/Massive, Alpha Vantage и другие были убраны из-за чувствительной регистрации, платного/закрытого доступа к опционам или неподходящей модели для статического приложения.

## Подсказки тикеров

- Локальные подсказки читаются из `data/index.json`:
  - `files` — тикеры с закэшированными цепочками.
  - `names` — тикер → название компании/фонда/индекса.
  - `no_options` — валидные тикеры, где последний скан не нашёл опционов; они показываются как **`(no options)`**.
- Yahoo, NASDAQ и CBOE используют endpoint прокси `/api/search?provider=...&q=...` для full-text поиска символов.
- DoltHub ищет тикеры SQL-запросом по историческому архиву.
- Поиск провайдера — это discovery helper: некоторые найденные символы всё равно могут вернуть "нет опционов" при загрузке.

## Greeks в static cache

Новые/обновлённые static cache файлы получают per-quote metadata `greeksSource`. Сборщик сначала берёт provider-supplied CBOE delayed greeks (`greeksSource: "cboe"`), а если CBOE не дал greeks, считает Black-Scholes estimate (`greeksSource: "black-scholes"`), когда есть spot/IV/expiration. Оставшиеся пропуски получают `greeksMissingReason`. Уже существующие файлы получат metadata по мере refresh workflow.

Доступные greeks: **Delta (Δ)**, **Gamma (Γ)**, **Theta (Θ)**, **Vega**, и **Rho (ρ)**. Rho отключён по умолчанию в настройках колонок.

## Публикация на GitHub Pages

1. Включи Pages: **Settings → Pages**.
2. Разреши Actions коммитить: **Settings → Actions → General → Workflow permissions → Read and write permissions**.
3. Workflow **Update options data** запускает `scripts/fetch_data.py`, сам находит universe тикеров, обновляет/расширяет `data/*.json`, обновляет `data/index.json` и коммитит изменения в `master`.
4. Workflow **GitHub Pages** собирает приложение через `bun run build-github-pages` и деплоит `dist/`.

Ручной список тикеров поддерживается только для разовых запусков: `TICKERS="AAPL MSFT SPY" python scripts/fetch_data.py`. Плановый workflow использует самообнаружение.

## Настройка прокси для GitHub Pages

**Важно:** При использовании GitHub Pages (или любого static host), провайдеры с прокси (Yahoo, NASDAQ, CBOE) требуют **локально запущенный прокси**, потому что браузер не может напрямую обращаться к этим API из-за CORS ограничений.

### Как это работает

1. Браузер загружает приложение с GitHub Pages (например, `https://daggerok.github.io/options-desk/`)
2. Когда выбираешь провайдера с прокси, приложение отправляет запросы на **Proxy base URL** (по умолчанию: `http://localhost:8787`)
3. Прокси (запущенный на твоей локальной машине) перенаправляет запросы на Yahoo/NASDAQ/CBOE и возвращает ответ
4. Это работает, потому что браузер может обращаться к `localhost` даже когда страница загружена с GitHub Pages

### Запуск локального прокси

```bash
# Клонируй репозиторий (если ещё не сделал)
git clone https://github.com/daggerok/options-desk.git
cd options-desk

# Установи зависимости
bun install -E

# Запусти прокси-сервер
bun ./scripts/yahoo-proxy.ts
```

Прокси запустится на `http://localhost:8787` по умолчанию.

### Настройка приложения

1. Открой приложение в браузере
2. Нажми на **иконку шестерёнки** (Settings) в правом верхнем углу
3. Найди поле **Proxy base URL**
4. Установи `http://localhost:8787` (или свой кастомный порт)
5. Теперь можно использовать Yahoo, NASDAQ и CBOE провайдеров

### Альтернатива: Cloudflare Worker

Для деплоя прокси без локального запуска:

1. Деплой `scripts/cloudflare-worker.js` на Cloudflare Workers
2. Установи **Proxy base URL** на URL твоего Worker (например, `https://your-worker.your-subdomain.workers.dev`)

### Решение проблем с прокси

- **"Could not reach the proxy"**: убедись, что прокси запущен (`bun ./scripts/yahoo-proxy.ts`)
- **CORS errors**: прокси должен быть запущен на `localhost` или деплоен как Cloudflare Worker
- **Port conflicts**: измени порт в `scripts/yahoo-proxy.ts` или используй переменную окружения `PORT`

## Вспомогательная инфраструктура

- `scripts/fetch_data.py` — умный yfinance-сборщик. Создаёт/обновляет `data/*.json`, обогащает greeks из CBOE delayed quotes плюс Black-Scholes fallback и ведёт `data/index.json` с `{ files, count, generated, names, no_options }`.
- `.github/workflows/update-data.yml` — плановый/ручной refresh данных.
- `scripts/yahoo-proxy.ts` — локальный **Bun**-прокси:
  - `/api/options` — Yahoo optionChain с crumb/cookies.
  - `/api/nasdaq` — relay NASDAQ option-chain.
  - `/api/cboe` — relay CBOE delayed-options.
  - `/api/search?provider=yahoo|nasdaq|cboe&q=...` — подсказки тикеров.
- `scripts/cloudflare-worker.js` — Cloudflare Worker с теми же provider endpoints плюс `/raw?url=...`.

## Структура проекта

```text
src/
  index.html                  # Parcel entry shell
  index.css                   # Tailwind v4, тема, scrollbars/CSS для доски
  main.tsx                    # React app, providers, UI, кэш/состояние
data/
  index.json                  # { files, count, generated, names, no_options }
  AAPL.json, SPY.json, ...    # один cache-файл цепочки на тикер, с greeks metadata после refresh
scripts/
  fetch_data.py               # yfinance -> data/*.json + data/index.json
  yahoo-proxy.ts              # локальный Bun proxy: Yahoo/NASDAQ/CBOE/search
  cloudflare-worker.js        # Cloudflare Worker: Yahoo/NASDAQ/CBOE/search/raw
.github/workflows/
  ci.yaml                     # build checks
  update-data.yml             # обновление данных по расписанию
  github-pages.yml            # деплой Pages
package.json                  # Bun/Parcel scripts
pyproject.toml                # Python deps для fetch_data.py
README.md                     # TOC с ссылками на README.en.md и README.ru.md
README.en.md                  # Английская документация
README.ru.md                  # Русская документация (этот файл)
```

## Приватность и ключи

- Настройки и токены в браузере хранятся только в `localStorage`.
- Backend отсутствует, если ты сам не запускаешь/деплоишь optional proxy.
- На общем компьютере очищай ключи/настройки через настройки приложения или storage браузера.
- Для публичного деплоя без токенов в браузере используй Static cache или свой Cloudflare Worker.

## Решение проблем

- **При открытии ничего не грузится:** это нормально. Нажми **Get dates**, затем **Load**.
- **Needs proxy / CORS:** запусти `bun ./scripts/yahoo-proxy.ts` локально или укажи Cloudflare Worker URL в Settings → Proxy base URL.
- **`Unexpected token '<'`:** прокси/сервер вернул HTML вместо JSON. Проверь URL прокси или провайдера.
- **Static cache говорит not cached:** тикера нет в `data/*.json`; используй другой провайдер или дождись, пока data workflow его закэширует.
- **Подсказка `(no options)`:** тикер валиден в локальном manifest, но последний скан не нашёл listed options.
- **DoltHub старый:** это ожидаемо; provider — исторический архив на `2024-11-11`.
- **Proxy connection refused:** убедись, что прокси запущен (`bun ./scripts/yahoo-proxy.ts`) и Proxy base URL указан правильно в Settings.

---

*Agentic developer note: keep this README synchronized with `src/main.tsx`, `src/index.css`, `scripts/*`, and `.github/workflows/*`. Prefer correcting/removing stale comments over preserving inaccurate ones.*
