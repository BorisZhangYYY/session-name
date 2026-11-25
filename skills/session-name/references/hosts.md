# Host adapters

Use only the section for the actual host, not an agent mentioned in the conversation. The paths are relative to the installed skill root. A host-native rename bound to the current session takes precedence if it also allows exact read-back.

## Hermes Agent

Run `python3 <skill-dir>/scripts/hermes.py --title='Exact title'` on the local host with the `hermes` CLI available. The script requires the host-provided `HERMES_SESSION_ID` and the owning profile’s absolute `HERMES_HOME`. It checks for an exact row and title collisions, calls `hermes sessions rename`, then independently queries the same ID in `state.db` in read-only mode. If the runtime uses a different ID, resolve it only through the host’s own current-session capability, or report a suggestion. If the system Python cannot read the SQLite store, use a newer Python/SQLite build or the one bundled with Hermes; never change the database's journal mode to make this script work. It refuses reserved `Bot Chat` titles.

## OpenClaw

Use the [native session tools](https://docs.openclaw.ai/concepts/session-tool). Before writing, use `session_status` without a `sessionKey` (native current-session default) and find the matching `sessions_list` row and `sessionId` using the exact key shown by the host. Ensure these are the active session, not its origin/delivery route. If `label` already matches, do not write. Call `sessions` with `action: "patch"` and `label: "Exact title"`; omit `sessionKey` to use the native current-session binding, and set `expectedSessionId` to the observed ID. Then independently read `sessions_list` and require that the same `key` and `sessionId` have the exact `label`. Use only metadata, and respect paging and tool limits. If you cannot establish the identity or verify read access before writing, the tool is missing, or the patch is rejected, report that you could not safely apply the title. Do not try a privileged gateway CLI or edit files instead.

## Claude Code

Run `python3 <skill-dir>/scripts/claude-code.py --title='Exact title'` from the real Claude Code Bash tool environment with `CLAUDE_CODE_SESSION_ID`. The Python environment must already have a [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/python) version exposing `get_session_info` and `rename_session`. The script checks the exact local session first and reads `custom_title` back after the change. No model turn is run. If the SDK is unavailable or the session is remote or not locally persisted, return suggestions. The live UI may need refreshing even after persisted metadata is verified.

## Codex

Run `node <skill-dir>/scripts/codex.mjs --title='Exact title'` only when `CODEX_THREAD_ID` is trusted for the current Codex session and refers to the local Codex store. Do not use inside a nested Codex process if it may have inherited its parent’s ID. The script uses [Codex App Server](https://developers.openai.com/codex/app-server) over stdio with the installed `codex` binary: `thread/read` → `thread/name/set` → `thread/read`, with no model turn and no history included. If the thread is ephemeral, remote, or inaccessible in the sandbox, report a suggestion; do not elevate permissions to work around a refusal. The live UI and persisted metadata may refresh at different times.

## DeepSeek Harness (DSH)

Resolve the skill directory from the resource location supplied by DSH’s skill loader. Use the common formatter and skill-local configuration. If the current profile already exposes a trusted, current-session-bound rename tool, use it. The optional third-party [dsh-set-session-title v0.1.1](https://github.com/CancerTiN/dsh-set-session-title/tree/v0.1.1) exposes `set_session_title` with a single `title` argument; do not install it during a naming request. This plugin can normalize or truncate titles, so keep generated titles concise and do not send an explicit user title unless the host can preserve it. Compare the exact returned title, then independently read the current title via an authorized host capability if one is available. The plugin’s `eventSeq` and returned title are a write receipt, not an independent read. If no independent read is available or the title differs, report what the host returned without calling it verified. If no rename tool is available, return suggestions and point to the session’s **Rename** menu in the DSH UI. Do not edit session logs or use private endpoints.

## Tencent WorkBuddy

Use the common formatter and configuration from this skill’s imported directory. If the task environment cannot run Node, read the default and optional override files to produce suggestions. Do not use another agent’s adapter or look for private task storage. No supported agent-facing rename interface has been verified for WorkBuddy, so provide the suggested title and, when the user asked to apply it, point to the current task’s **⋯ / right-click → 重命名** menu. Do not say the title was applied. This is a desktop skill-import path, not a claim of cloud task compatibility.
