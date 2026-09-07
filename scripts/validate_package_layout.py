#!/usr/bin/env python3
"""Reject ambiguous sample directories in official Skill source packages."""
import argparse
from pathlib import Path


def validate(root):
    errors = []
    for skill in sorted(root.iterdir()):
        if not skill.is_dir():
            continue
        if not (skill / 'SKILL.md').is_file():
            errors.append(f'{skill.name}: missing SKILL.md')
        if (skill / 'examples').exists():
            errors.append(f'{skill.name}: examples/ is forbidden; executable fixtures belong in cases/, explanatory samples in references/')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path, default=Path(__file__).resolve().parents[1] / 'skills')
    args = parser.parse_args()
    errors = validate(args.skills_root)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('PACKAGE_LAYOUT_OK')


if __name__ == '__main__':
    main()
