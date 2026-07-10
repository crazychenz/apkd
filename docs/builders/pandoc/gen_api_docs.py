#!/usr/bin/env python3
"""Generate docs/api/api-reference.md from docs/api/api-spec.json.

This stands in for a real docstring extractor (e.g. something walking a
Python AST and pulling Google-style docstrings). The important part for the
pipeline is the *shape* of what it emits:

  - one H2 per namespace (class/module), listed + numbered in the TOC
  - a member-summary table per namespace, every name linking to its anchor
  - one H4 per member, `.unlisted .unnumbered` so hundreds of methods don't
    flood the table of contents, but every single one still carries a
    stable `#id` anchor that can be linked to from anywhere
  - a THICK `{.namespace-rule}` divider between namespaces
  - a THIN `{.member-rule}` divider between the member table and the member
    bodies, and between each member body

Also writes a JSON build report (--debug-json) listing every anchor emitted,
useful for CI to diff against previous runs or to verify no anchors were
accidentally duplicated/renamed (which would silently break cross-links).
"""
import argparse
import json
import sys
from pathlib import Path


def render_description(paragraph_lines: list[str]) -> str:
    return " ".join(line.strip() for line in paragraph_lines if line.strip())


def render_member(m: dict) -> str:
    parts = []
    parts.append(f"#### `{m['name']}` {{#{m['id']} .unlisted .unnumbered}}")
    parts.append("")
    parts.append(f"`{m['signature']}`")
    parts.append("")
    parts.append(render_description(m["description"]))

    if m.get("args"):
        parts.append("")
        parts.append("**Args:**")
        parts.append("")
        for a in m["args"]:
            parts.append(f"- `{a['name']}` (`{a['type']}`): {a['desc']}")

    if m.get("returns"):
        parts.append("")
        parts.append(f"**Returns:** {m['returns']}")

    if m.get("raises"):
        parts.append("")
        parts.append("**Raises:**")
        parts.append("")
        for r in m["raises"]:
            parts.append(f"- `{r['type']}`: {r['desc']}")

    parts.append("")
    return "\n".join(parts)


def render_namespace(ns: dict, anchors: list[dict]) -> str:
    parts = []
    parts.append(f"## {ns['name']} {{#{ns['id']}}}")
    anchors.append({"id": ns["id"], "kind": ns["kind"], "name": ns["name"], "type": "namespace"})
    parts.append("")
    parts.append(f"*({ns['kind']})* `{ns['signature']}`")
    parts.append("")
    parts.append(render_description(ns["description"]))
    parts.append("")

    parts.append("| Name | Kind | Summary |")
    parts.append("| --- | --- | --- |")
    for m in ns["members"]:
        parts.append(f"| [`{m['name']}`](#{m['id']}) | {m['kind']} | {m['summary']} |")
    parts.append("")

    parts.append(":::: {.member-rule}\n::::")
    parts.append("")

    for i, m in enumerate(ns["members"]):
        parts.append(render_member(m))
        anchors.append({"id": m["id"], "kind": m["kind"], "name": m["name"], "type": "member",
                        "namespace": ns["id"]})
        if i != len(ns["members"]) - 1:
            parts.append(":::: {.member-rule}\n::::")
            parts.append("")

    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--debug-json", type=Path, default=None)
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))

    anchors: list[dict] = []
    sections = []
    sections.append("# API Reference\n")
    sections.append(
        "This chapter is generated in full by `scripts/gen_api_docs.py` from "
        "`docs/api/api-spec.json`. Do not hand-edit this file; edit the spec "
        "(or, in a real pipeline, the source docstrings) and regenerate.\n"
    )

    namespaces = spec["namespaces"]
    for i, ns in enumerate(namespaces):
        sections.append(render_namespace(ns, anchors))
        if i != len(namespaces) - 1:
            sections.append(":::: {.namespace-rule}\n::::\n")

    output_text = "\n".join(sections).rstrip() + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_text, encoding="utf-8")
    print(f"wrote: {args.output} ({len(namespaces)} namespaces, {len(anchors)} anchors)")

    if args.debug_json:
        args.debug_json.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "source_spec": str(args.spec),
            "output_file": str(args.output),
            "namespace_count": len(namespaces),
            "anchor_count": len(anchors),
            "anchors": anchors,
        }
        dupes = [a["id"] for a in anchors]
        seen = set()
        duplicate_ids = sorted({d for d in dupes if d in seen or seen.add(d)})
        report["duplicate_anchor_ids"] = duplicate_ids
        args.debug_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"debug report: {args.debug_json}")
        if duplicate_ids:
            print(f"WARNING: duplicate anchor ids found: {duplicate_ids}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
