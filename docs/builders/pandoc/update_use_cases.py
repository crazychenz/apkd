#!/usr/bin/env python3
"""Regenerate the `nightly-benchmarks` GENERATED block in advanced-usage.md.

This simulates a pre-processing step that pulls fresh data (here: a fixture
standing in for a CI artifact) and rewrites *only* the content between the
`<!-- GENERATED:BEGIN ... -->` / `<!-- GENERATED:END ... -->` markers, so
hand-written prose around it is never touched or clobbered.

Usage:
    scripts/update_use_cases.py docs/guides/advanced-usage.md
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

# Stand-in for "fetch the latest CI benchmark artifact". In a real pipeline
# this would hit an API, read a JSON artifact, or query a database.
FIXTURE_BENCHMARKS = {
    "run_id": "#4822",
    "rows": [
        {"scenario": "cold start", "throughput": 829, "p99": "112 ms"},
        {"scenario": "warm cache", "throughput": 5104, "p99": "8 ms"},
        {"scenario": "batch (1k)", "throughput": 63870, "p99": "4 ms"},
    ],
}

MARKER_RE = re.compile(
    r"(<!-- GENERATED:BEGIN {name} -->\n)(.*?)(\n<!-- GENERATED:END {name} -->)",
    re.DOTALL,
)


def render_block(data: dict) -> str:
    lines = ["| Scenario | Throughput (widgets/s) | p99 latency |", "| --- | --- | --- |"]
    for row in data["rows"]:
        lines.append(f"| {row['scenario']} | {row['throughput']:,} | {row['p99']} |")
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append("")
    lines.append(f"_Last refreshed: {timestamp} from CI run `{data['run_id']}`._")
    return "\n".join(lines)


def update_file(path: Path, name: str, data: dict) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        MARKER_RE.pattern.format(name=re.escape(name)), re.DOTALL
    )
    match = pattern.search(text)
    if not match:
        print(f"error: markers for '{name}' not found in {path}", file=sys.stderr)
        return False

    new_block = render_block(data)
    new_text = text[: match.start(2)] + new_block + text[match.end(2) :]
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"updated: {path} ({name})")
    else:
        print(f"unchanged: {path} ({name})")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="markdown file containing the marker block")
    parser.add_argument("--marker-name", default="nightly-benchmarks")
    parser.add_argument(
        "--debug-json",
        type=Path,
        default=None,
        help="if set, dump the fixture data used for this run as JSON for troubleshooting",
    )
    args = parser.parse_args()

    if args.debug_json:
        args.debug_json.parent.mkdir(parents=True, exist_ok=True)
        args.debug_json.write_text(json.dumps(FIXTURE_BENCHMARKS, indent=2), encoding="utf-8")

    ok = update_file(args.file, args.marker_name, FIXTURE_BENCHMARKS)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
