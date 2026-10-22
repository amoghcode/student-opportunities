#!/usr/bin/env python3
"""Validate the canonical YAML records and prepare data for the static site."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_data import ROOT, load_yaml, validate


def main() -> int:
    errors, warnings = validate(ROOT)
    for warning in warnings:
        print(f"WARNING {warning}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"Site data was not built: {len(errors)} validation error(s).")
        return 1

    opportunities_dir = ROOT / "opportunities"
    records = [
        load_yaml(path)
        for path in sorted(opportunities_dir.glob("*.yml"))
        if not path.name.startswith("_")
    ]
    output = ROOT / "site" / "opportunities.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(records)} opportunity record(s) for the website.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
