import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { parseArgs } from 'node:util';

async function rename(threadId, name) {
  const child = spawn('codex', ['app-server', '--listen', 'stdio://'], { stdio: ['pipe', 'pipe', 'ignore'] });
  const lines = createInterface({ input: child.stdout });
  let sequence = 0;
  let stopped;
  const pending = new Map();
  function fail(error) {
    stopped = error;
    for (const { reject } of pending.values()) reject(error);
    pending.clear();
  }
  child.on('error', fail);
  child.on('exit', (code, signal) => fail(new Error(`Codex app-server exited (${code ?? signal})`)));
  child.stdin.on('error', fail);
  lines.on('line', (line) => {
    let message;
    try { message = JSON.parse(line); } catch { return; }
    if (!message || message.method || !pending.has(message.id)) return;
    const { resolve, reject, method } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(`${method}: ${message.error.message}`));
    else resolve(message.result);
  });
  function send(message) {
    if (stopped) throw stopped;
    child.stdin.write(`${JSON.stringify(message)}\n`);
  }
  function call(method, params) {
    return new Promise((resolve, reject) => {
      if (stopped) { reject(stopped); return; }
      const id = ++sequence;
      pending.set(id, { resolve, reject, method });
      send({ id, method, params });
    });
  }
  async function read() {
    const { thread } = await call('thread/read', { threadId, includeTurns: false });
    if (thread?.id !== threadId) throw new Error('No exact Codex thread was returned');
    return thread.name;
  }
  const timer = setTimeout(() => fail(new Error('Codex app-server timed out')), 20_000);
  try {
    await call('initialize', { clientInfo: { name: 'session-name', version: '0.0.1' } });
    send({ method: 'initialized' });
    if (await read() === name) return 'unchanged';
    await call('thread/name/set', { threadId, name });
    if (await read() !== name) throw new Error('Rename requested, but the same thread did not read back with the exact title');
    return 'renamed';
  } finally {
    clearTimeout(timer);
    lines.close();
    child.stdin.end();
    child.kill();
  }
}

try {
  const { values } = parseArgs({ options: { title: { type: 'string' }, help: { type: 'boolean' } } });
  if (values.help) console.log('Usage: node scripts/codex.mjs --title TITLE (requires trusted CODEX_THREAD_ID)');
  else {
    const threadId = process.env.CODEX_THREAD_ID ?? '';
    if (!/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(threadId)) {
      throw new Error('Trusted current CODEX_THREAD_ID (UUID) is required');
    }
    const { title } = values;
    if (!title || title !== title.trim() || /[\p{Cc}\u2028\u2029]/u.test(title)) {
      throw new Error('Title must be a nonempty single line without leading/trailing whitespace or control characters');
    }
    const status = await rename(threadId, title);
    console.log(JSON.stringify({ status, sessionId: threadId, title }));
  }
} catch (error) {
  console.error(`session-name: ${error.message}`);
  process.exitCode = 1;
}
