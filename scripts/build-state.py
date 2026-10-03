#!/usr/bin/env python3
"""Identify builds by release AND patch/CI revision, not just upstream version."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(tag: str) -> str:
    digest = hashlib.sha256(tag.encode())
    paths = sorted((ROOT / 'patch').glob('*.patch')) + sorted((ROOT / 'scripts').glob('*'))
    paths += [ROOT / '.github/workflows/auto-build.yml']
    for path in paths:
        if path.is_file():
            digest.update(str(path.relative_to(ROOT)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+-]*', args.tag):
        parser.error('missing or invalid upstream release tag')
    key = fingerprint(args.tag)
    try:
        previous = json.loads((ROOT / 'last_built.json').read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        previous = {}
    should_build = args.force or previous.get('fingerprint') != key
    with open(args.output, 'a') as output:
        output.write(f'tag={args.tag}\nfingerprint={key}\nshould_build={str(should_build).lower()}\n')
    print(f'{args.tag}: ' + ('build required' if should_build else 'same successful build; skip'))


if __name__ == '__main__':
    main()
