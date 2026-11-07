#!/usr/bin/env python3
"""Check skill and agent frontmatter. With --stale, list artifacts due for review."""

import argparse
import datetime
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
AGENT_FIELDS = {"name", "description", "metadata"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STALE_AFTER_DAYS = 90


def artifacts():
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        yield skill, skill.parent.name, True
    for agent in sorted((ROOT / "agents").glob("*.md")):
        yield agent, agent.stem, False


def frontmatter(path):
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("no frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("unterminated frontmatter") from None
    data = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def problems(data, expected_name, is_skill):
    name = data.get("name")
    if name != expected_name:
        yield f"name {name!r} does not match {expected_name!r}"
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
        yield "name must be lowercase letters, digits and hyphens, max 64 characters"
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        yield "description is missing"
    elif len(description) > 1024:
        yield "description is longer than 1024 characters"
    extra = set(data) - (SKILL_FIELDS if is_skill else AGENT_FIELDS)
    if extra:
        yield f"non-standard fields: {', '.join(sorted(extra))} (move them under metadata)"
    metadata = metadata_of(data)
    if metadata is None:
        yield "metadata must be a mapping"
        return
    if not metadata.get("owner"):
        yield "metadata.owner is missing"
    if verified_on(metadata) is None:
        yield "metadata.last-verified must be a YYYY-MM-DD date"


def metadata_of(data):
    metadata = data.get("metadata") or {}
    return metadata if isinstance(metadata, dict) else None


def verified_on(metadata):
    value = metadata.get("last-verified")
    if isinstance(value, datetime.datetime):
        return None
    if isinstance(value, datetime.date):
        return value
    if not isinstance(value, str) or not DATE_RE.match(value):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stale", action="store_true", help="list artifacts not verified in 90 days")
    args = parser.parse_args()

    failed = False
    cutoff = datetime.date.today() - datetime.timedelta(days=STALE_AFTER_DAYS)
    for path, expected_name, is_skill in artifacts():
        rel = path.relative_to(ROOT)
        try:
            data = frontmatter(path)
        except (ValueError, yaml.YAMLError) as error:
            print(f"{rel}: {error}")
            failed = True
            continue
        if args.stale:
            metadata = metadata_of(data) or {}
            verified = verified_on(metadata)
            if verified is None or verified < cutoff:
                print(f"{rel}: last verified {verified or 'never'}, owner {metadata.get('owner', 'none')}")
            continue
        for problem in problems(data, expected_name, is_skill):
            print(f"{rel}: {problem}")
            failed = True

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
