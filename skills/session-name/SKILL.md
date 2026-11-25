---
name: session-name
description: Use when naming sessions. Apply configurable prefixes.
license: MIT
metadata:
  author: BorisZhangYYY
  version: '0.0.1'
---

# Name the current session

## When to Use

Use only when asked to name or rename the current session. If asked for suggestions only, do not use a rename tool. A complete title explicitly supplied by the user takes precedence: apply it verbatim or explain if the host cannot preserve it. A one-off naming format does not edit the saved config.

1. For generated titles, read the effective categories and template with `node <skill-dir>/scripts/title.mjs config`; resolve `<skill-dir>` relative to this skill, not the project directory. See [default categories](references/prefixes.json) and [configuration](references/configuration.md). User overrides live in `references/config.json` next to the defaults. If Node is unavailable, read the defaults and any user config directly and provide suggestions without writing. If user config is invalid, explain the error rather than silently using defaults. A user-supplied exact title does not require the formatter or its config.
2. Choose one category based on the conversation’s main goal, not just the last turn. Prefer `bugfix` for unexpected behavior, `feat` for a concrete new capability, `discuss` for weighing options, and `learn` for building understanding. Follow the configured descriptions for custom categories. Use the configured fallback only when no category fits. Write a short, searchable topic in the conversation’s language; retain distinguishing project, feature, or issue names. Format the primary title and one or two alternatives with `node <skill-dir>/scripts/title.mjs format --type <category> --topic <topic>`. Pass values as separate, safely quoted arguments. Default example: `[feat] 支持自定义会话前缀`.
3. If applying a title, prefer a host-native tool bound to the current session; otherwise follow the relevant section of the [host adapters](references/hosts.md). Only change the current session’s display title and verify the exact target and title by reading them back. Never guess an ID, use a recent-session heuristic, edit a session database/transcript directly, or work around permissions. Do not create or resume a session just to rename it.
4. Report the title as applied only if verified. If the rename was requested but verification failed, explicitly say the outcome is unverified; do not retry blindly. If the host cannot safely change the title, report a suggestion only and state why. Mark the alternatives as not applied.
