# Documentation Pipeline (Pandoc Markdown -> Typst -> PDF / HTML / CommonMark)

A worked demonstration of a docs pipeline where:

- Content is authored as Pandoc Markdown files in a Docusaurus-shaped
  `docs/` tree.
- A **PDF** is built by concatenating every source file into **one** Pandoc
  pass, converting Markdown -> Typst, then compiling Typst -> PDF, so the
  table of contents and cross-references are computed correctly across the
  whole manual.
- **HTML** can be built either as one monolithic page or as a multi-page
  tree (one pandoc pass per file), because both are legitimate targets and
  they need different link-rewriting.
- **CommonMark** is rendered **per file**, preserving the folder structure,
  ready to be dropped straight into a Docusaurus `docs/` directory.
- Authors write cross-file links the same way (`[text](../other.md#anchor)`)
  regardless of target; a Lua filter rewrites them per-build.
- Some headings can opt out of the table of contents without being deleted
  from the page, via a `.unlisted` class.
- The API reference is generated wholesale from a spec (standing in for
  extracted docstrings); use-case docs mix hand-written prose with a
  narrower block that's mechanically refreshed in place.

## Layout

```
docs/                       content, mirrors a Docusaurus docs/ folder
  intro.md                  hand-written
  guides/
    getting-started.md      hand-written
    advanced-usage.md       hand-written prose + one GENERATED:... block
  api/
    api-spec.json           input to the API doc generator
    api-reference.md         *** generated, do not hand-edit ***

template/
  manual.typst               custom Pandoc template for the `typst` writer
                              (title page, hyperlinked+depth-limited TOC,
                              running header, H1 rule styling)

filters/
  toc-control.lua            .unlisted / .unnumbered heading classes
  crosslink.lua               rewrites cross-file links per build target
  rules.lua                   .namespace-rule / .member-rule -> thick/thin hr

scripts/
  build.sh                   orchestrates everything (see below)
  gen_api_docs.py             api-spec.json -> api-reference.md
  update_use_cases.py         refreshes the GENERATED block in-place

assets/
  manual.css                  styling for HTML output, incl. thick/thin rules

build/                        all pipeline output (gitignored in a real repo)
  manual.pdf
  manual.html                 monolithic HTML
  html-multipage/              one .html per source file, same tree shape
  commonmark/                  one .md per source file, Docusaurus-ready
  debug/                       JSON/log troubleshooting artifacts
```

## Running it

```bash
scripts/build.sh          # everything
scripts/build.sh pdf      # just the PDF
scripts/build.sh html     # monolithic + multi-page HTML
scripts/build.sh commonmark
```

Every run first executes the pre-processors (`update_use_cases.py`,
`gen_api_docs.py`) so the generated content is always fresh before any
format is rendered. `build/debug/build-summary.json` (plus a handful of
`*-stderr.log` and `--trace` files alongside it) is written on every run for
troubleshooting.

Requires `pandoc` (3.x; must include Lua-filter support and the `typst`
writer, both standard since Pandoc 3.1) and, for the final PDF step,
[`typst`](https://github.com/typst/typst) on `PATH`. If `typst` isn't
installed, `build.sh pdf` still produces `build/manual.typ` and tells you
the exact `typst compile` command to run once you've installed it.

## Authoring conventions

### Cross-file links

Always write them as a normal relative Markdown link with an explicit
anchor:

```markdown
See [the setup guide](../guides/getting-started.md#install-the-cli).
```

`filters/crosslink.lua` rewrites the target based on `-M crosslink_mode=...`:

| Mode              | Used for                     | `other.md#anchor` becomes |
| ----------------- | ----------------------------- | -------------------------- |
| `internal`         | PDF, monolithic HTML          | `#anchor` (in-doc reference) |
| `html-multipage`   | multi-page HTML                | `other.html#anchor`        |
| `commonmark`       | Docusaurus CommonMark tree     | left untouched              |

A cross-file link with **no anchor** works fine for `html-multipage` and
`commonmark`, but can't be resolved in `internal` mode (there's no Typst
label for "the top of another file" once everything's merged into one
document) — the filter logs a warning to stderr and leaves it as a literal
string link rather than silently producing a dead link. Always give
cross-file link targets an explicit `#anchor` and this never comes up.

### Keeping a heading out of the Table of Contents

```markdown
## Internal migration notes {.unlisted}
```

The heading still renders normally in the body and still gets a real anchor
(`#internal-migration-notes`) you can link to. It just won't appear as a
TOC/outline entry in the PDF or HTML. Add `.unnumbered` too if you also
don't want a section number:

```markdown
#### `process_batch` {#acmewidget-process_batch .unlisted .unnumbered}
```

This is exactly how the API reference generator keeps hundreds of member
headings out of the manual's outline while still giving every single one a
stable, linkable anchor.

**Limitation:** CommonMark/Docusaurus has no equivalent concept — its
right-hand-side "on this page" outline is generated from every heading with
no per-heading opt-out. `toc-control.lua` strips the `.unlisted`/
`.unnumbered` classes for the CommonMark target (so Docusaurus's `{#id}`
heading-id parser, which expects a bare id and nothing else, still works)
but the heading will still show up in Docusaurus's own on-page TOC. If that
matters, consider `toc_min_heading_level`/`toc_max_heading_level` front
matter in the Docusaurus file, or restructure so overly-granular headings
(like individual API members) live in Docusaurus's own generated API pages
rather than as literal Markdown headings.

### Namespace / member separators (API docs)

```markdown
:::: {.namespace-rule}
::::

:::: {.member-rule}
::::
```

`filters/rules.lua` turns these into a thick or thin rule appropriately for
whichever writer is active (a raw Typst `#line(...)` for the PDF, a raw
`<hr class="...">` — styled in `assets/manual.css` — for both HTML modes and
for CommonMark, since Docusaurus's MDX renders bare HTML tags fine).

### Generated content

Two different patterns are demonstrated on purpose, because they solve
different problems:

- **Whole-file generation** (`docs/api/api-reference.md`): the entire file
  is owned by `scripts/gen_api_docs.py`; never hand-edit it. This is the
  right shape when a preprocessor has the complete picture (e.g. a
  docstring extractor knows every namespace/member up front).
- **In-place block generation** (`docs/guides/advanced-usage.md`): only the
  region between `<!-- GENERATED:BEGIN name -->` / `<!-- GENERATED:END
  name -->` markers is rewritten; hand-written prose around it is
  untouched. This is the right shape for a page that's mostly narrative but
  has one section (a benchmark table, a changelog snippet, a live example)
  that needs to stay fresh.

## Why the PDF path needs a single Pandoc pass

Typst's `#outline()` and Pandoc's own `--toc` handling both work by walking
the *whole* document they're given. Feeding Pandoc all the source files at
once (`pandoc intro.md guides/*.md api/api-reference.md -t typst ...`) means
Pandoc concatenates them into a single AST before any writer or filter sees
it, so the TOC, the `.unlisted` accounting, and any future index/glossary
you add are all computed correctly over the entire manual in one shot.
Rendering file-by-file (as the CommonMark/multi-page-HTML paths do, on
purpose, since Docusaurus and static multi-page HTML both want independent
files) would give you a separate, incomplete TOC per file instead.

One consequence: heading identifiers must be **unique across the whole
manual**, since they all land in one Typst label namespace once merged.
Pandoc auto-generates ids by slugifying heading text and *does* disambiguate
accidental collisions by appending `-1`, `-2`, etc., but relying on that is
fragile for anything you intend to link to — give anything you'll reference
an explicit `{#id}` (as every API member above does) rather than trusting
the auto-slug.

## Debug / troubleshooting artifacts

Every build writes to `build/debug/`:

- `api-gen-report.json` — every anchor the API generator emitted, plus a
  `duplicate_anchor_ids` check.
- `use-case-refresh.json` — the fixture data used to refresh the benchmark
  table, so you can see exactly what a given build run pulled in.
- `pdf-pandoc-stderr.log` — Pandoc's own `--trace` output (a line per parse/
  filter event) plus any warnings, redirected to this file for each build
  step.
- `pdf-typst-stderr.log` — `typst compile` diagnostics, when `typst` is
  installed.
- `build-summary.json` — pandoc/typst version info plus a manifest of every
  debug artifact from the run, useful as a single file to attach to a bug
  report.
