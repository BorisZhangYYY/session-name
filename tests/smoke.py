"""Opt-in integration checks. Write only disposable sessions in an explicit scratch root."""

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'session-name'
TITLE = "[feat] 会话命名验证"


def run(args, env, expected="renamed"):
    result = subprocess.run(args, cwd=SKILL, env=env, capture_output=True, text=True, timeout=35)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr or result.stdout}")
    receipt = json.loads(result.stdout)
    assert receipt["status"] == expected and receipt["title"] == TITLE, receipt
    print(f"{Path(args[1]).name}: {expected} and exact title verified")
    return receipt["sessionId"]


def hermes(base):
    home = base / "hermes"
    home.mkdir()
    sid = '20261125_123000_test1234'
    env = dict(os.environ, HERMES_HOME=str(home), HERMES_SESSION_ID=sid)
    repo = os.environ["SESSION_NAME_HERMES_REPO"]
    python = os.environ["SESSION_NAME_HERMES_PYTHON"]
    seed = """import hermes_bootstrap
import os
from pathlib import Path
from persistence_assembly import open_persistence, profile_scope
from persistence.conversation.sessions import NewSession
from persistence.conversation.messages import NewMessage
with open_persistence(profile_scope(home=Path(os.environ['HERMES_HOME'])), eager=True) as store:
    sid = store.sessions.create(NewSession(session_id='20261125_123000_test1234', source='cli'))
    store.messages.append(sid, NewMessage.from_live({'role': 'user', 'content': 'Disposable session'}))
"""
    subprocess.run([python, '-c', seed], cwd=repo, env=env, check=True, timeout=30)
    assert (home / 'state.db').is_file(), list(home.iterdir())
    # Use the same modern Python/SQLite build as the installed Hermes runtime.
    cmd = [python, 'scripts/hermes.py', '--title=' + TITLE]
    assert run(cmd, env) == sid
    assert run(cmd, env, 'unchanged') == sid
    malformed = subprocess.run([python, 'scripts/hermes.py', '--title=has  two spaces'],
                               cwd=SKILL, env=env, capture_output=True, text=True, timeout=30)
    assert malformed.returncode != 0 and 'cannot preserve' in malformed.stderr, malformed
    assert run(cmd, env, 'unchanged') == sid
    env['HERMES_SESSION_ID'] = sid[:-2]
    refused = subprocess.run(cmd, cwd=SKILL, env=env, capture_output=True, text=True, timeout=30)
    assert refused.returncode != 0 and 'No exact session' in refused.stderr, refused
    print('hermes.py: refused a partial ID without mutation')


def claude(base):
    home = base / "claude"
    project = home / "projects" / "-disposable-project"
    project.mkdir(parents=True)
    sid = str(uuid.uuid4())
    entry = {"type": "user", "sessionId": sid, "uuid": str(uuid.uuid4()), "parentUuid": None,
             "isSidechain": False, "cwd": "/disposable/project",
             "message": {"role": "user", "content": "Disposable session"}}
    (project / (sid + '.jsonl')).write_text(json.dumps(entry) + '\n', encoding='utf8')
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(home), CLAUDE_CODE_SESSION_ID=sid)
    cmd = [sys.executable, 'scripts/claude-code.py', '--title=' + TITLE]
    assert run(cmd, env) == sid
    assert run(cmd, env, 'unchanged') == sid


def codex(base):
    home = base / 'codex'
    home.mkdir()
    sid = str(uuid.uuid4())
    # A small legacy rollout fixture lets the real app-server perform the
    # rename without contacting a model, or touching the user's Codex store.
    folder = home / 'sessions' / '2026' / '11' / '25'
    folder.mkdir(parents=True)
    stamp = '2026-11-25T12:30:00.000Z'
    meta = {'type': 'session_meta', 'timestamp': stamp, 'payload': {
        'id': sid, 'timestamp': stamp, 'cwd': str(ROOT), 'originator': 'codex_cli_rs',
        'cli_version': '0.166.0', 'source': 'cli', 'model_provider': 'openai',
    }}
    event = {'type': 'event_msg', 'timestamp': stamp, 'payload': {
        'type': 'user_message', 'message': 'Disposable session', 'images': [], 'local_images': [], 'text_elements': [],
    }}
    rollout = folder / f'rollout-2026-11-25T12-30-00-{sid}.jsonl'
    rollout.write_text(''.join(json.dumps(row) + '\n' for row in (meta, event)), encoding='utf8')
    env = dict(os.environ, CODEX_HOME=str(home), CODEX_THREAD_ID=sid)
    cmd = ['node', 'scripts/codex.mjs', '--title=' + TITLE]
    assert run(cmd, env) == sid
    assert run(cmd, env, 'unchanged') == sid


def openclaw(base):
    """Verify Gateway label persistence, not the agent's native-tool permissions."""
    binary = os.environ.get('SESSION_NAME_OPENCLAW_CLI')
    cli = ['node', binary] if binary else ['openclaw']
    env = {k: v for k, v in os.environ.items() if k in {'PATH', 'LANG', 'TMPDIR', 'SYSTEMROOT'}}
    env.update(HOME=str(base), OPENCLAW_STATE_DIR=str(base / 'state'),
               OPENCLAW_NO_RESPAWN='1', OPENCLAW_SKIP_CHANNELS='1',
               XDG_CONFIG_HOME=str(base / 'config'), DISABLE_TELEMETRY='1')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'ws://127.0.0.1:{port}'
    token = uuid.uuid4().hex

    def rpc(method, data):
        result = subprocess.run(cli + ['gateway', 'call', method, '--url', url,
                                       '--token', token, '--params', json.dumps(data), '--json'],
                                env=env, cwd=base, capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise RuntimeError('OpenClaw call failed: ' + result.stderr.replace(token, '[redacted]'))
        return json.loads(result.stdout)

    with (base / 'gateway.log').open('w+', encoding='utf8') as log:
        gateway = subprocess.Popen(cli + ['gateway', 'run', '--allow-unconfigured', '--bind', 'loopback',
                                          '--port', str(port), '--auth', 'token', '--token', token],
                                   env=env, cwd=base, stdout=log, stderr=log)
        try:
            for _ in range(80):
                if gateway.poll() is not None:
                    break
                try:
                    with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                        break
                except OSError:
                    time.sleep(0.25)
            else:
                raise RuntimeError('OpenClaw smoke gateway did not start')
            if gateway.poll() is not None:
                log.seek(0)
                raise RuntimeError(log.read().replace(token, '[redacted]'))
            created = rpc('sessions.create', {'label': 'Disposable session'})
            key = created['key']
            before = rpc('sessions.describe', {'key': key})
            row = before.get('session', before)
            sid = row['sessionId']
            rpc('sessions.patch', {'key': key, 'expectedSessionId': sid, 'label': TITLE})
            after = rpc('sessions.describe', {'key': key})
            row = after.get('session', after)
            assert row['sessionId'] == sid and row['label'] == TITLE, row
            print('OpenClaw gateway: renamed and read back the exact session label')
        finally:
            if gateway.poll() is None:
                gateway.terminate()
                try:
                    gateway.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    gateway.kill()
                    gateway.wait(timeout=5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('host', choices=['hermes', 'claude', 'codex', 'openclaw'])
    parser.add_argument('--scratch', required=True, type=Path)
    options = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='session-name-', dir=options.scratch.resolve(strict=True)) as folder:
        globals()[options.host](Path(folder))
