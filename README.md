# Options Desk [![CI](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml/badge.svg)](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml)

A single-page **options board**: enter a ticker, get expirations, select one or more dates, and view the classic **Calls | Strike | Puts** chain with bid / mid / ask, IV, volume, open interest and greeks where the provider supplies them. The app is a static React + TypeScript + Tailwind CSS v4 site built by Parcel and deployable to GitHub Pages.

> **RU:** Одностраничная **опционная доска**: вводишь тикер, получаешь даты экспираций, выбираешь одну или несколько дат и смотришь цепочку **Calls | Strike | Puts** с bid / mid / ask, IV, объёмом, OI и греками там, где источник их отдаёт. Приложение статическое: React + TypeScript + Tailwind CSS v4, сборка Parcel, деплой на GitHub Pages.

---

## Table of contents / Оглавление

- [English (full documentation)](docs/README.en.md)
  - [What you get](docs/README.en.md#what-you-get)
  - [Quick start](docs/README.en.md#quick-start)
  - [How to use](docs/README.en.md#how-to-use)
  - [Data providers](docs/README.en.md#data-providers)
  - [Ticker suggestions](docs/README.en.md#ticker-suggestions)
  - [Static-cache greeks](docs/README.en.md#static-cache-greeks)
  - [Deploy to GitHub Pages](docs/README.en.md#deploy-to-github-pages)
  - [Proxy setup for GitHub Pages](docs/README.en.md#proxy-setup-for-github-pages)
  - [Companion infrastructure](docs/README.en.md#companion-infrastructure)
  - [Project structure](docs/README.en.md#project-structure)
  - [Privacy & keys](docs/README.en.md#privacy--keys)
  - [Troubleshooting](docs/README.en.md#troubleshooting)
- [Русская документация](docs/README.ru.md)
  - [Что это умеет](docs/README.ru.md#что-это-умеет)
  - [Быстрый старт](docs/README.ru.md#быстрый-старт)
  - [Как пользоваться](docs/README.ru.md#как-пользоваться)
  - [Провайдеры данных](docs/README.ru.md#провайдеры-данных)
  - [Подсказки тикеров](docs/README.ru.md#подсказки-тикеров)
  - [Greeks в static cache](docs/README.ru.md#greeks-в-static-cache)
  - [Публикация на GitHub Pages](docs/README.ru.md#публикация-на-github-pages)
  - [Настройка прокси для GitHub Pages](docs/README.ru.md#настройка-прокси-для-github-pages)
  - [Вспомогательная инфраструктура](docs/README.ru.md#вспомогательная-инфраструктура)
  - [Структура проекта](docs/README.ru.md#структура-проекта)
  - [Приватность и ключи](docs/README.ru.md#приватность-и-ключи)
  - [Решение проблем](docs/README.ru.md#решение-проблем)

---

*Agentic developer note: This is an Agentic AI-developed project. Agents must always start by reading [AGENT.md](./AGENT.md) as the main entry point and contract. Keep these READMEs synchronized with `src/main.tsx`, `src/index.css`, `scripts/*`, and `.github/workflows/*`. Prefer correcting/removing stale comments over preserving inaccurate ones.*

---

## Agentic Setup

This repository is optimized for AI-agentic development. It includes:
- [AGENT.md](./AGENT.md): Main agent contract and rules (English).
- [AGENT.ru.md](./docs/AGENT.ru.md): Main agent contract and rules (Russian).
- [CLAUDE.md](./CLAUDE.md): Adapter for Claude Code.
- [.cursorrules](./.cursorrules): Rules for Cursor AI.
- [Setup.md](./docs/Setup.md): Tutorial on setting up agentic workflows.
- [ARENA.md](./ARENA.md): Specific rules for Arena.ai.
- [DEVELOPMENT.md](./docs/DEVELOPMENT.md): Detailed developer guide.

We use **Bun** for JavaScript/TypeScript and **uv** for Python to ensure fast and reproducible environments.
