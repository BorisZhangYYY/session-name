"""Rename exactly the current local Claude Code session via Anthropic's Agent SDK."""

import argparse
import json
import os
import re
import sys
import unicodedata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    title = parser.parse_args().title
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", sid):
        parser.error("Trusted current CLAUDE_CODE_SESSION_ID (UUID) is required")
    if not title or title != title.strip() or any(
        unicodedata.category(char) in {"Cc", "Zl", "Zp"} for char in title
    ):
        parser.error("Title must be a nonempty single line without leading/trailing whitespace or control characters")
    try:
        from claude_agent_sdk import get_session_info, rename_session
    except ImportError:
        print("session-name: Claude Agent SDK with get_session_info and rename_session is required", file=sys.stderr)
        return 1
    try:
        before = get_session_info(sid)
        if before is None or before.session_id != sid:
            raise ValueError("No exact local Claude Code session found")
        status = "unchanged"
        if before.custom_title != title:
            rename_session(sid, title)
            after = get_session_info(sid)
            if after is None or after.session_id != sid or after.custom_title != title:
                raise ValueError("Rename requested, but the same session did not read back with the exact title")
            status = "renamed"
    except (OSError, ValueError) as exc:
        print(f"session-name: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": status, "sessionId": sid, "title": title}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
