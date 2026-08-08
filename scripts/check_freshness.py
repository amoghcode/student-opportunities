#!/usr/bin/env python3
"""Report records that should be manually re-verified."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def months_until(current_month: int, target_month: int) -> int:
    return (target_month - current_month) % 12


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--fail-after-days", type=int, default=0, help="fail when a record exceeds this age; zero only reports")
    args = parser.parse_args()

    stale = 0
    priority = 0
    checked = 0
    for path in sorted((ROOT / "opportunities").glob("*.yml")):
        if path.name.startswith("_"):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        checked += 1
        verified = date.fromisoformat(data["last_verified"])
        age = (args.as_of - verified).days
        level = "current"
        if age > 365:
            level = "needs-verification"
            stale += 1
        elif age > 180:
            level = "aging"

        schedule = data.get("schedule", {})
        typical = schedule.get("typical_open_months", [])
        current_or_next_month = any(months_until(args.as_of.month, month) <= 1 for month in typical)
        announced_future = any(
            cycle.get("opens_on") and date.fromisoformat(cycle["opens_on"]) >= args.as_of
            for cycle in schedule.get("cycles", [])
        )
        if data.get("lifecycle") == "active" and current_or_next_month and not announced_future:
            level = f"{level}, priority-cycle-review"
            priority += 1
        print(f"{level.upper():35} {path.name} — verified {verified.isoformat()} ({age} days ago)")

    print(f"Reviewed {checked} record(s): {stale} stale, {priority} priority cycle review(s).")
    return 1 if args.fail_after_days and any(
        (args.as_of - date.fromisoformat(yaml.safe_load(p.read_text(encoding='utf-8'))['last_verified'])).days > args.fail_after_days
        for p in (ROOT / 'opportunities').glob('*.yml') if not p.name.startswith('_')
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())

