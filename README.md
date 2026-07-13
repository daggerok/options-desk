# Options Desk [![CI](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml/badge.svg)](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml)

A single-page **options board** with English / Russian interface: enter a ticker, get expirations, select one or more dates, and view the classic **Calls | Strike | Puts** chain with bid / mid / ask, IV, volume, open interest and greeks where the provider supplies them. The app is a static React + TypeScript + Tailwind CSS v4 site built by Parcel and deployable to GitHub Pages.

> **RU:** Одностраничная **опционная доска** с интерфейсом на английском / русском языке: вводишь тикер, получаешь даты экспираций, выбираешь одну или несколько дат и смотришь цепочку **Calls | Strike | Puts** с bid / mid / ask, IV, объёмом, OI и греками там, где источник их отдаёт. Приложение статическое: React + TypeScript + Tailwind CSS v4, сборка Parcel, деплой на GitHub Pages.

---

## Documentation / Документация

| Document / Документ | English | Русский |
|---|---|---|
| Overview & usage | [`docs/README.en.md`](docs/README.en.md) | [`docs/README.ru.md`](docs/README.ru.md) |
| Developer guide | [`docs/DEVELOPMENT.en.md`](docs/DEVELOPMENT.en.md) | [`docs/DEVELOPMENT.ru.md`](docs/DEVELOPMENT.ru.md) |
| Agentic-setup how-to | [`docs/Setup.en.md`](docs/Setup.en.md) | [`docs/Setup.ru.md`](docs/Setup.ru.md) |
| Arena.ai adapter | [`docs/ARENA.en.md`](docs/ARENA.en.md) | [`docs/ARENA.ru.md`](docs/ARENA.ru.md) |
| `AGENTS.md` compat stub | [`docs/AGENTS.en.md`](docs/AGENTS.en.md) | [`docs/AGENTS.ru.md`](docs/AGENTS.ru.md) |

---

*Agentic developer note: This is an Agentic AI-developed project. Agents must always start by reading [AGENT.md](./AGENT.md) as the main entry point and contract. Keep these READMEs synchronized with `src/main.tsx`, `src/index.css`, `scripts/*`, and `.github/workflows/*`. Prefer correcting/removing stale comments over preserving inaccurate ones.*

---

## Agentic Setup

This repository is optimized for AI-agentic development. Core agent files stay in the repository root; extended guides live in [`./docs`](./docs).

- [AGENT.md](./AGENT.md): Main agent contract and rules (главный контракт, RU).
- [CLAUDE.md](./CLAUDE.md): Adapter for Claude Code.
- [docs/.cursorrules](./docs/.cursorrules): Rules for Cursor AI.
- [docs/Setup.en.md](./docs/Setup.en.md) / [docs/Setup.ru.md](./docs/Setup.ru.md): Tutorial on setting up agentic workflows.
