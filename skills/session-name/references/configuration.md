# Configure title prefixes

The built-in [prefixes.json](prefixes.json) ships with the skill. For your settings, create or edit `references/config.json` **inside the installed `session-name` skill**. The formatter loads it relative to the script, not the project directory. If it is absent, the built-in values are used. No global config or environment variable is required.

Do not edit `prefixes.json`: it is managed by the release. Keep a backup of `config.json` before reinstalling or updating with a tool that replaces the skill directory. Multiple agent paths linked to the same installation share the same `config.json`; independent copies can use different settings. If you used an earlier local build, you can copy your old override into `references/config.json`; the old path is no longer read.

Example `references/config.json`:

```json
{
  "template": "[{type}] {topic}",
  "defaultType": "research",
  "prefixes": {
    "research": "Design experiments and validate hypotheses.",
    "work": "Coordinate a delivery or cross-team work item.",
    "chore": null
  }
}
```

- New names extend the defaults, strings replace an existing description, and `null` disables a category. Names use lowercase ASCII letters or digits with optional hyphens. `defaultType` must name an enabled category.
- `{type}` is the category key, `{topic}` the required topic, and `{date}` the local calendar date (`YYYYMMDD`). Use `"template": "{date}-{topic}"` for the old format, or `"[{type}] {date} {topic}"` to show both.
- `node scripts/title.mjs config` shows the effective settings. `node scripts/title.mjs format --type bugfix --topic '修复登录超时'` previews the title without changing any session.
