import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

function run(t, args, config, envOverrides = {}) {
  const dir = mkdtempSync(join(tmpdir(), 'session-name-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const skill = join(dir, 'session-name');
  const cwd = join(dir, 'unrelated-project');
  mkdirSync(cwd);
  mkdirSync(join(skill, 'scripts'), { recursive: true });
  mkdirSync(join(skill, 'references'));
  for (const file of ['scripts/title.mjs', 'references/prefixes.json']) {
    copyFileSync(new URL(`../skills/session-name/${file}`, import.meta.url), join(skill, file));
  }
  if (config !== undefined) writeFileSync(join(skill, 'references', 'config.json'), JSON.stringify(config));
  const env = { ...process.env, HOME: dir, XDG_CONFIG_HOME: dir, ...envOverrides };
  delete env.SESSION_NAME_CONFIG;
  return spawnSync(process.execPath, [join(skill, 'scripts', 'title.mjs'), ...args], {
    cwd, env, encoding: 'utf8',
  });
}

test('built-in bugfix category renders a searchable title without a date', (t) => {
  const result = run(t, ['format', '--type', 'bugfix', '--topic', '修复登录超时']);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '[bugfix] 修复登录超时');
});

test('user categories extend defaults and date supports the legacy format', (t) => {
  const result = run(t, ['format', '--type', 'research', '--topic', 'Agent 压测', '--date', '20261125'], {
    prefixes: { research: 'A research investigation' }, template: '{date}-{topic}',
  });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '20261125-Agent 压测');
});

test('removing a category makes it unavailable without removing other defaults', (t) => {
  const config = { prefixes: { feat: null, research: 'Explore a question' } };
  const result = run(t, ['config'], config);
  assert.equal(result.status, 0, result.stderr);
  const resolved = JSON.parse(result.stdout);
  assert.equal('feat' in resolved.prefixes, false);
  assert.ok(resolved.prefixes.learn);
  assert.equal(resolved.prefixes.research, 'Explore a question');
});

test('unknown category fails closed and prints no title', (t) => {
  const result = run(t, ['format', '--type', 'unknown', '--topic', 'Something']);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /unknown category/i);
  assert.equal(result.stdout, '');
});

test('local calendar date comes from the tool runtime timezone', (t) => {
  const timeZone = 'Asia/Shanghai';
  const date = () => new Intl.DateTimeFormat('fr-CA', { timeZone, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()).replace(/-/g, '');
  const before = date();
  const result = run(t, ['format', '--topic', '主题'], { template: '{date}-{topic}' }, { TZ: timeZone });
  assert.equal(result.status, 0, result.stderr);
  assert.ok([`${before}-主题`, `${date()}-主题`].includes(result.stdout.trim()));
});

test('a malformed template is rejected before printing a title', (t) => {
  const result = run(t, ['format', '--topic', 'Theme'], { template: '[{typo}] {topic}' });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /unknown template placeholder/i);
  assert.equal(result.stdout, '');
});

test('multiline topic is rejected before printing a title', (t) => {
  const result = run(t, ['format', '--topic', 'Line\nBreak']);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /single line/i);
  assert.equal(result.stdout, '');
});

test('default config is used when the implicit config file is absent', (t) => {
  const result = run(t, ['format', '--topic', 'Schema choices']);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '[discuss] Schema choices');
});

test('explicit day must be a valid calendar date', (t) => {
  const result = run(t, ['format', '--topic', 'Release', '--date', '20260230']);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /valid YYYYMMDD calendar date/);
});
