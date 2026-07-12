# AGENTS.md

Этот файл добавлен для совместимости с агентами, которые ищут именно `AGENTS.md`.

Основные правила проекта находятся в [`AGENT.md`](./AGENT.md). Для Claude-специфичного поведения см. [`CLAUDE.md`](./CLAUDE.md).

Коротко:

- отвечать пользователю по-русски;
- работать через Spec → Verifier → Environment;
- начинать новые задачи от актуального `origin/master`;
- не коммитить build/cache artifacts;
- не менять workflow-файлы без явного разрешения и token с `workflow` scope;
- после изменений запускать релевантные проверки;
- stale comments исправлять, а не сохранять ради истории;
- провайдеры только CACHE / CBOE / NASDAQ / YAHOO (порядок фиксирован; localhost default CBOE, Pages default CACHE).
