# Options Desk [![CI](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml/badge.svg)](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml)

A single-page **options board**: enter a ticker, get expirations, select one or more dates, and view the classic **Calls | Strike | Puts** chain with bid / mid / ask, IV, volume, open interest and greeks where the provider supplies them. The app is a static React + TypeScript + Tailwind CSS v4 site built by Parcel and deployable to GitHub Pages.

> **RU:** Одностраничная **опционная доска**: вводишь тикер, получаешь даты экспираций, выбираешь одну или несколько дат и смотришь цепочку **Calls | Strike | Puts** с bid / mid / ask, IV, объёмом, OI и греками там, где источник их отдаёт. Приложение статическое: React + TypeScript + Tailwind CSS v4, сборка Parcel, деплой на GitHub Pages.

---

## Table of contents / Оглавление

- [English (full documentation)](README.en.md)
  - [What you get](README.en.md#what-you-get)
  - [Quick start](README.en.md#quick-start)
  - [How to use](README.en.md#how-to-use)
  - [Data providers](README.en.md#data-providers)
  - [Ticker suggestions](README.en.md#ticker-suggestions)
  - [Static-cache greeks](README.en.md#static-cache-greeks)
  - [Deploy to GitHub Pages](README.en.md#deploy-to-github-pages)
  - [Proxy setup for GitHub Pages](README.en.md#proxy-setup-for-github-pages)
  - [Companion infrastructure](README.en.md#companion-infrastructure)
  - [Project structure](README.en.md#project-structure)
  - [Privacy & keys](README.en.md#privacy--keys)
  - [Troubleshooting](README.en.md#troubleshooting)
- [Русская документация](README.ru.md)
  - [Что это умеет](README.ru.md#что-это-умеет)
  - [Быстрый старт](README.ru.md#быстрый-старт)
  - [Как пользоваться](README.ru.md#как-пользоваться)
  - [Провайдеры данных](README.ru.md#провайдеры-данных)
  - [Подсказки тикеров](README.ru.md#подсказки-тикеров)
  - [Greeks в static cache](README.ru.md#greeks-в-static-cache)
  - [Публикация на GitHub Pages](README.ru.md#публикация-на-github-pages)
  - [Настройка прокси для GitHub Pages](README.ru.md#настройка-прокси-для-github-pages)
  - [Вспомогательная инфраструктура](README.ru.md#вспомогательная-инфраструктура)
  - [Структура проекта](README.ru.md#структура-проекта)
  - [Приватность и ключи](README.ru.md#приватность-и-ключи)
  - [Решение проблем](README.ru.md#решение-проблем)

---

*Agentic developer note: keep these READMEs synchronized with `src/main.tsx`, `src/index.css`, `scripts/*`, and `.github/workflows/*`. Prefer correcting/removing stale comments over preserving inaccurate ones.*
