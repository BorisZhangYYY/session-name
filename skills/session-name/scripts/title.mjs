import { readFileSync } from 'node:fs';
import { parseArgs } from 'node:util';

const defaults = new URL('../references/prefixes.json', import.meta.url);
const userConfig = new URL('../references/config.json', import.meta.url);
const controls = /[\p{Cc}\u2028\u2029]/u;
const category = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
const slots = new Set(['type', 'topic', 'date']);

function singleLine(value, field) {
  if (typeof value !== 'string' || !value.trim() || controls.test(value)) {
    throw new Error(`${field} must be a nonempty single line without control characters`);
  }
}

function object(value, field) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${field} must be an object`);
  return value;
}

function config() {
  let raw;
  try { raw = readFileSync(userConfig, 'utf8'); } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const base = JSON.parse(readFileSync(defaults, 'utf8'));
  const override = raw === undefined ? {} : object(JSON.parse(raw), 'references/config.json');
  for (const key of Object.keys(override)) {
    if (!Object.hasOwn(base, key)) throw new Error(`Unknown config field: ${key}`);
  }
  const merged = { ...base, ...override };
  const prefixes = new Map(Object.entries(base.prefixes));
  if (Object.hasOwn(override, 'prefixes')) {
    for (const [key, value] of Object.entries(object(override.prefixes, 'prefixes'))) {
      if (!category.test(key)) throw new Error(`Invalid category: ${key}`);
      if (value === null) prefixes.delete(key);
      else {
        singleLine(value, `Category description (${key})`);
        prefixes.set(key, value);
      }
    }
  }
  if (!prefixes.has(merged.defaultType)) throw new Error('defaultType must name an enabled category');
  singleLine(merged.template, 'template');
  for (const match of merged.template.matchAll(/\{([^{}]+)\}/g)) {
    if (!slots.has(match[1])) throw new Error(`Unknown template placeholder: ${match[0]}`);
  }
  if (!merged.template.includes('{topic}') || /[{}]/.test(merged.template.replace(/\{[^{}]+\}/g, ''))) {
    throw new Error('template must include {topic} and cannot contain unmatched braces');
  }
  return { ...merged, prefixes: Object.fromEntries(prefixes) };
}

function localDate() {
  const today = new Date();
  return [today.getFullYear(), today.getMonth() + 1, today.getDate()]
    .map((part, index) => String(part).padStart(index ? 2 : 4, '0')).join('');
}

function calendarDate(date) {
  if (/^\d{8}$/.test(date)) {
    const parsed = new Date(`${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6)}T00:00:00Z`);
    if (Number.isFinite(+parsed) && parsed.toISOString().slice(0, 10).replaceAll('-', '') === date) return date;
  }
  throw new Error('date must be a valid YYYYMMDD calendar date');
}

try {
  const [command, ...args] = process.argv.slice(2);
  if (!args.length && command === '--help') {
    console.log('Usage: node scripts/title.mjs config | format --topic TOPIC [--type TYPE] [--date YYYYMMDD]');
  } else if (command === 'config' && !args.length) {
    console.log(JSON.stringify(config(), null, 2));
  } else if (command === 'format') {
    const { values } = parseArgs({ args, options: { type: { type: 'string' }, topic: { type: 'string' }, date: { type: 'string' } } });
    const { template, defaultType, prefixes } = config();
    const type = values.type ?? defaultType;
    if (!Object.hasOwn(prefixes, type)) throw new Error(`Unknown category: ${type}`);
    singleLine(values.topic, 'topic');
    const date = values.date === undefined ? localDate() : calendarDate(values.date);
    console.log(template.replace(/\{(type|topic|date)\}/g, (_, slot) => ({ type, topic: values.topic.trim(), date })[slot]).trim());
  } else {
    throw new Error('Expected config or format (see --help)');
  }
} catch (error) {
  console.error(`session-name: ${error.message}`);
  process.exitCode = 1;
}
