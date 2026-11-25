"""Rename exactly the current Hermes session via the host CLI; SQLite is read-only."""

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import unicodedata


def read_title(db, session_id, new_title):
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as connection:
        connection.execute("PRAGMA query_only = ON")
        rows = connection.execute(
            "SELECT id, title FROM sessions WHERE id = ? OR title = ?",
            (session_id, new_title),
        ).fetchall()
    current = next((row for row in rows if row[0] == session_id), None)
    if current is None:
        raise ValueError("No exact session in this Hermes profile; refusing to resolve by name or prefix")
    if any(row[0] != session_id for row in rows):
        raise ValueError("Another session already has this title; choose a different title")
    return current[1]


def rename(title):
    sid = os.environ.get("HERMES_SESSION_ID", "")
    home = os.environ.get("HERMES_HOME")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", sid) or not home or not Path(home).is_absolute():
        raise ValueError("Trusted current HERMES_SESSION_ID and absolute HERMES_HOME are required")
    # Reject titles the host would normalize before writing, so an explicit
    # title is either preserved or not applied at all.
    invisible = r"[\u200b-\u200f\u2028-\u202e\u2060-\u2069\ufeff\ufffc\ufff9-\ufffb]"
    if (not title or title != " ".join(title.split()) or re.search(invisible, title)
            or any(unicodedata.category(char) in {"Cc", "Cs"} for char in title)):
        raise ValueError("Hermes cannot preserve this title's whitespace or invisible characters")
    db = (Path(home) / "state.db").resolve()
    before = read_title(db, sid, title)
    if before == title:
        return "unchanged", sid
    # Some older Hermes releases did not enforce the dedicated Bot Chat name.
    if before == "Bot Chat" or title == "Bot Chat":
        raise ValueError("Refusing to change a reserved Bot Chat title")
    result = subprocess.run(
        ["hermes", "sessions", "rename", "--", sid, title],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode:
        raise ValueError("Hermes did not confirm the rename: " + (result.stderr or result.stdout).strip())
    if read_title(db, sid, title) != title:
        raise ValueError("Rename requested, but the same session did not read back with the exact title")
    return "renamed", sid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    try:
        status, sid = rename(args.title)
    except (OSError, ValueError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(f"session-name: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": status, "sessionId": sid, "title": args.title}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
