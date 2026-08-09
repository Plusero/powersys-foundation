#!/usr/bin/env python3
"""Enforce the executable-Python contract for every Quarto tutorial."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"

FRONT_MATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
PYTHON_CELL = re.compile(
    r"^```\{python\}\s*\n(?P<body>.*?)^```\s*$",
    re.DOTALL | re.MULTILINE,
)


def check_article(path: Path) -> list[str]:
    """Return policy violations for one tutorial."""
    text = path.read_text(encoding="utf-8")
    violations: list[str] = []

    front_matter_match = FRONT_MATTER.match(text)
    if front_matter_match is None:
        return ["missing YAML front matter"]

    metadata = front_matter_match.group("body")
    if re.search(r"^jupyter:\s*python3\s*$", metadata, re.MULTILINE) is None:
        violations.append("front matter must declare `jupyter: python3`")

    categories = re.search(r"^categories:\s*(.+)$", metadata, re.MULTILINE)
    if categories is None or "Python" not in categories.group(1):
        violations.append("front matter categories must include `Python`")

    if re.search(r"^execute:\s*false\s*$", metadata, re.MULTILINE):
        violations.append("document-level execution cannot be disabled")

    cells = [match.group("body") for match in PYTHON_CELL.finditer(text)]
    if not cells:
        violations.append("must contain at least one executable `{python}` cell")
    elif all(
        re.search(r"^#\|\s*eval:\s*false\s*$", cell, re.MULTILINE)
        for cell in cells
    ):
        violations.append("at least one Python cell must not set `eval: false`")

    return violations


def main() -> int:
    tutorials = sorted(ARTICLES.glob("*.qmd"))
    if not tutorials:
        print("No tutorials found in articles/.", file=sys.stderr)
        return 1

    failures = {
        path.relative_to(ROOT): violations
        for path in tutorials
        if (violations := check_article(path))
    }

    if failures:
        print("Tutorial Python companion check failed:", file=sys.stderr)
        for path, violations in failures.items():
            for violation in violations:
                print(f"  - {path}: {violation}", file=sys.stderr)
        return 1

    print(
        f"Checked {len(tutorials)} tutorials: each has an executable Python companion."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
