# Options Desk [![CI](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml/badge.svg)](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml)

A single-page **options board** with English / Russian interface: enter a ticker, get expirations, select one or more dates, and view the classic **Calls | Strike | Puts** chain with bid / mid / ask, IV, volume, open interest and greeks where the provider supplies them. The app is a static React + TypeScript + Tailwind CSS v4 site built by Parcel and deployable to GitHub Pages.

> **RU:** Одностраничная **опционная доска** с интерфейсом на английском / русском языке: вводишь тикер, получаешь даты экспираций, выбираешь одну или несколько дат и смотришь цепочку **Calls | Strike | Puts** с bid / mid / ask, IV, объёмом, OI и греками там, где источник их отдаёт. Приложение статическое: React + TypeScript + Tailwind CSS v4, сборка Parcel, деплой на GitHub Pages.

---

## Documentation / Документация

- [English documentation](docs/README.en.md)
- [Русская документация](docs/README.ru.md)

---

*Agentic developer note: This is an Agentic AI-developed project. Agents must always start by reading [AGENT.md](./AGENT.md) as the main entry point and contract. Keep these READMEs synchronized with `src/main.tsx`, `src/index.css`, `scripts/*`, and `.github/workflows/*`. Prefer correcting/removing stale comments over preserving inaccurate ones.*

---

## Agentic Setup

This repository is optimized for AI-agentic development. Core agent files stay in the repository root; extended guides live in [`./docs`](./docs).

- [AGENT.md](./AGENT.md): Main agent contract and rules.
- [CLAUDE.md](./CLAUDE.md): Adapter for Claude Code.
- [docs/.cursorrules](./docs/.cursorrules): Rules for Cursor AI.
- [docs/Setup.md](./docs/Setup.md): Tutorial on setting up agentic workflows.
