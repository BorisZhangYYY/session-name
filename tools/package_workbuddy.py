"""Export the WorkBuddy desktop edition from the shared session-name skill."""

import argparse
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

SKILL = Path(__file__).resolve().parents[1] / 'skills' / 'session-name'
FILES = (
    'SKILL.md', 'LICENSE', 'references/prefixes.json', 'references/configuration.md',
    'references/hosts.md', 'scripts/title.mjs',
)


def export(output):
    files = {name: (SKILL / name).read_bytes() for name in FILES}
    # The shared workflow links to hosts.md. Keep that link valid, but do not
    # advertise adapters that are intentionally absent from this edition.
    hosts = files['references/hosts.md'].decode('utf-8')
    match = re.search(r'^## Tencent WorkBuddy\n.*?(?=^## |\Z)', hosts, re.M | re.S)
    if not match:
        raise ValueError('WorkBuddy host instructions are missing')
    files['references/hosts.md'] = ('# Host adapters\n\n' + match[0].rstrip() + '\n').encode('utf-8')
    with ZipFile(output, 'x', compression=ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr('session-name/' + name, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new ZIP file (existing files are not overwritten)')
    args = parser.parse_args()
    try:
        export(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'package_workbuddy: {error}\n')
    print(args.output.resolve())


if __name__ == '__main__':
    main()
