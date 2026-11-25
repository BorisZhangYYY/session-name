# Changelog

## v0.0.1 — Initial release

- Name the current Agent session by its main topic. The default format is `[type] topic`, with nine built-in categories including `bugfix`, `feat`, `discuss`, and `learn`.
- Add, replace, or disable categories using the skill-local `references/config.json`. Customize the title template, including opting back into `YYYYMMDD-topic`.
- Apply the chosen title through the host's supported interface and verify the exact session and title. Offer one or two unapplied alternatives. Suggestion-only requests never write; explicit titles bypass generation.
- Install the shared MIT-licensed skill via `npx skills` for Hermes Agent, OpenClaw, Claude Code, and Codex. Only `skills/session-name/` is installed; repository tests and release docs are excluded. Host prerequisites and behavior are documented in [host adapters](skills/session-name/references/hosts.md).
- Verified isolated installation for all four hosts and rename/read-back with Hermes, Claude Code's SDK, and Codex. OpenClaw label persistence was verified at the Gateway level; in-chat tool access depends on the host's permissions and was not tested end to end.
- Documented DeepSeek Harness skill discovery and optional current-session rename tool integration. Added a WorkBuddy desktop ZIP export with title suggestions and a manual rename fallback.
