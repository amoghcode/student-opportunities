#!/usr/bin/env python3
"""Probe dataset URLs without changing records."""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "StudentOpportunitiesLinkChecker/0.1 (+repository maintenance)"


@dataclass(frozen=True)
class Result:
    url: str
    status: int | None
    outcome: str
    detail: str


def collect_urls() -> list[str]:
    urls: set[str] = set()
    for path in (ROOT / "opportunities").glob("*.yml"):
        if path.name.startswith("_"):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for key in ("official_url", "application_url"):
            if data.get(key):
                urls.add(data[key])
        urls.update(source["url"] for source in data.get("verification_sources", []))
    return sorted(urls)


def request(url: str, method: str) -> tuple[int, str]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.status, response.geturl()


def check(url: str) -> Result:
    last_error = ""
    for attempt in range(2):
        for method in ("HEAD", "GET"):
            try:
                status, final_url = request(url, method)
                detail = f"redirects to {final_url}" if final_url.rstrip("/") != url.rstrip("/") else "ok"
                return Result(url, status, "ok", detail)
            except urllib.error.HTTPError as exc:
                if exc.code in {401, 403, 405, 429}:
                    if exc.code == 405 and method == "HEAD":
                        continue
                    return Result(url, exc.code, "warning", "access restricted or automated checks blocked")
                last_error = str(exc)
                if method == "HEAD":
                    continue
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = str(exc)
                break
        if attempt == 0:
            time.sleep(1)
    return Result(url, None, "failed", last_error)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--fail-on-broken", action="store_true")
    args = parser.parse_args()
    urls = collect_urls()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
        results = list(executor.map(check, urls))
    failed = [result for result in results if result.outcome == "failed"]
    for result in results:
        print(f"{result.outcome.upper():7} {result.status or '-':>3} {result.url} — {result.detail}")
    print(f"Checked {len(results)} URL(s): {len(failed)} failed.")
    return 1 if failed and args.fail_on_broken else 0


if __name__ == "__main__":
    sys.exit(main())

