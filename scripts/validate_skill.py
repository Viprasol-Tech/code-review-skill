#!/usr/bin/env python3
"""Validate the code-review Agent Skill.

Pure standard-library checks (no third-party deps):

  1. skill.md exists and opens with a YAML-style `---` frontmatter block.
  2. The frontmatter contains a `name:` field.
  3. The frontmatter contains a `description:` field of at least 40 characters.
  4. An examples/ directory exists with at least one `.md` file.

Exits 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

MIN_DESCRIPTION_LEN = 40

# Repo root = parent of this script's directory (scripts/..).
ROOT = Path(__file__).resolve().parent.parent


def fail(errors: list[str]) -> int:
    print("Skill validation FAILED:")
    for err in errors:
        print(f"  - {err}")
    return 1


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return the key/value pairs of a leading `---` frontmatter block.

    Returns None if the text does not start with a `---` fence and a matching
    closing `---`.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body = lines[1:i]
            break
    else:
        return None

    fields: dict[str, str] = {}
    for line in body:
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    errors: list[str] = []

    skill_path = ROOT / "skill.md"
    if not skill_path.is_file():
        return fail([f"skill.md not found at {skill_path}"])

    text = skill_path.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    if fields is None:
        errors.append("skill.md must start with a '---' frontmatter block "
                      "closed by a matching '---'.")
    else:
        name = fields.get("name", "")
        if not name:
            errors.append("frontmatter is missing a non-empty 'name:' field.")

        description = fields.get("description", "")
        if not description:
            errors.append("frontmatter is missing a 'description:' field.")
        elif len(description) < MIN_DESCRIPTION_LEN:
            errors.append(
                f"'description:' must be >= {MIN_DESCRIPTION_LEN} chars "
                f"(got {len(description)})."
            )

    examples_dir = ROOT / "examples"
    if not examples_dir.is_dir():
        errors.append("examples/ directory not found.")
    else:
        md_files = list(examples_dir.glob("*.md"))
        if not md_files:
            errors.append("examples/ must contain at least one .md file.")

    if errors:
        return fail(errors)

    print("Skill validation OK:")
    print(f"  - skill.md frontmatter: name='{fields['name']}', "
          f"description={len(fields['description'])} chars")
    print(f"  - examples/: {len(list((ROOT / 'examples').glob('*.md')))} "
          ".md file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
