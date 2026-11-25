# session-name

[Chinese README](docs/README.zh-CN.md)

Give your current Agent session a short, searchable title. The skill picks a category from the conversation and uses the `[type] topic` format, for example:

- `[bugfix] Fix login timeouts`
- `[feat] Add custom title prefixes`
- `[discuss] Compare session storage options`
- `[learn] Understand the Codex App Server`

## Install

For **Hermes Agent, OpenClaw, Claude Code, and Codex**, clone or download the repository, then run the [Skills CLI](https://github.com/vercel-labs/skills) from its root (Node.js 22+ recommended):

```sh
npx skills@1.7.4 add . --skill session-name -g -a hermes-agent openclaw claude-code codex -y
```

Omit any Agents you do not use. The CLI installs the complete `skills/session-name/` directory; `-a` selects where it goes, not which adapters it contains. Installation neither runs the adapters nor installs their dependencies. For a custom Hermes profile, copy the skill into that profile's `$HERMES_HOME/skills/`. If Hermes already has `session-name` under a category, update that copy instead of installing a second one.

### DeepSeek Harness (DSH)

Copy `skills/session-name/` into `$DSH_HOME/skills/` (default: `~/.dsh/skills/`) or into the project's `.dsh/skills/`. DSH also [discovers skills in the shared directory](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md). To use it from the repository root:

```sh
npx skills@1.7.4 add . --skill session-name -g -a universal -y
```

A shared copy already present at `~/.agents/skills/session-name/` does not need to be installed twice. Invoke `/session-name` in DSH.

### Tencent WorkBuddy

Download `session-name-v0.0.1-workbuddy.zip` from the [v0.0.1 release](https://github.com/BorisZhangYYY/session-name/releases/tag/v0.0.1). In the desktop app, go to **Experts, Skills & Connectors → Skills → Add Skill → Upload Skill** and import the ZIP. For project-scoped use, the [documented project path](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project) is `.codebuddy/skills/session-name/`.

To build the ZIP locally (it excludes other hosts' rename scripts and personal settings):

```sh
python3 tools/package_workbuddy.py session-name-workbuddy.zip
```

## Use

Ask your Agent to “Name this session,” or invoke `/session-name` if your host supports it. Ask for “suggestions only” to avoid changing the title, or supply an exact title to skip the template. When a rename can be verified, the skill reports the applied title and offers one or two unapplied alternatives.

| Agent | Rename behavior |
| --- | --- |
| Hermes Agent | Uses the official `hermes sessions rename` CLI and reads back the exact session. |
| OpenClaw | Uses the native session tools to set and read back the current session label, where permitted. |
| Claude Code | Uses the Claude Agent SDK to rename and read back the local session. Install the SDK separately (`python -m pip install claude-agent-sdk==0.2.189` in the Python environment used by the adapter). |
| Codex | Uses the local Codex App Server to rename and read back the current thread. |
| DeepSeek Harness | Suggests a title by default. Can apply it if a trusted current-session tool such as the optional `set_session_title` is already available. |
| Tencent WorkBuddy | Suggests a title for manual application through the current task's **Rename** menu. |

See [host details](skills/session-name/references/hosts.md) for prerequisites and read-back behavior. Hermes, Claude Code, and Codex were tested against disposable sessions. OpenClaw was tested at the gateway level; DSH desktop loading and WorkBuddy desktop import were not tested end to end.

## Customize

Create `references/config.json` inside the installed skill to add or disable categories, pick a fallback category, or change the template. For example, `"template": "{date}-{topic}"` restores date-based titles. If the file is absent, [the shipped defaults](skills/session-name/references/prefixes.json) apply. Back up your overrides before reinstalling with a tool that replaces the directory. See the [configuration guide](skills/session-name/references/configuration.md) for examples.

## Repository layout

- [`skills/session-name/`](skills/session-name/) — the installable skill, including its workflow, references, and scripts.
- [`tools/`](tools/) — WorkBuddy packaging; not part of the installed skill.
- [`tests/`](tests/) — run `node --test tests/*.test.mjs` and `python3 -m unittest discover -s tests` from the repository root.

[Changelog](CHANGELOG.md) · [MIT License](LICENSE)
