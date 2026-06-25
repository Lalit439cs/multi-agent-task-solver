# The Lab-Wiki pattern — what it is and how to reuse it

A portable note on the `WIKI.md` format used in this repo, written so you can drop
the same pattern into any other project. The blank template (`WIKI.md`) and a
self-contained append script (`log.sh`) live alongside this file.

## The core idea

It's a **"Karpathy-style" engineering wiki** — a single living document that is the
project's growing brain. It deliberately avoids heavyweight ADRs (Architecture
Decision Records). The whole design rests on one split:

| Zone                       | Behavior                                          | Holds                                              |
| -------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| **Anchor sections** (top)  | **Edited in place** — always reflects current truth | Architecture, Conventions, Gotchas, Open Questions, Index |
| **Log section** (bottom)   | **Append-only, newest-on-top, never edited**      | Dated entries preserving the journey / the why     |

The tension this resolves: anchors stay scannable as "what is true now," while the
Log preserves *how you got there*. When something changes, you **edit the anchor
AND append a Log entry** — never just one.

## The structure (top → bottom)

```
# Lab Wiki — <project>
> blockquote explaining the anchor/log rule

## Quick links          ← table of contents (anchor links)
---
## Architecture         ← what's true NOW about how it's built; each bullet → "see Log <date>"
## Diagrams             ← Mermaid for the few subtle flows; "update prose AND diagram together"
## Active Conventions   ← rules any contributor must currently honor
## Gotchas              ← sharp edges (starts empty, fills from real pain)
## Open Questions       ← pending decisions, each w/ [HIGH|MED|LOW] + revisit trigger + next step
## Run Index            ← one line per experiment/milestone, newest on top
---
## Log                  ← append-only journal, newest on top, dated ### headings + tags
```

Start minimal: `## Architecture`, `## Active Conventions`, `## Open Questions`, and
`## Log` are enough. Add `Diagrams` / `Gotchas` / `Run Index` only when you need them.

## The two rules that make it work

1. **Concreteness rule** — every Log entry must contain a number, step, or measured
   value. *"Switched LR"* is banned; *"LR 1e-4 → 3e-5 because loss diverged at step
   1200"* is required. This is what turns a diary into a research log.
2. **Log-before-act** — write the decision *before* you do it, so the entry surfaces
   assumptions instead of rationalizing after.

Each Log entry also carries a short **tag** (e.g. `*data-analysis-handoff*`) so
anchors can cross-reference back to the entry that explains them.

## How to reuse in another project

1. **Copy `WIKI.md`** into the repo root and fill in the project name + first few
   anchor bullets.
2. **Copy `log.sh`** (it's self-contained — pure bash/awk, no dependencies) and run
   `./log.sh "<entry>"` to append dated entries.
3. **Adopt the two disciplines** above (concreteness + log-before-act).
4. **Cross-link** anchors → Log entries by date/tag, so "current truth" always has a
   trail to "why."

## How it differs from neighbours

- **vs README** — a README describes the project to *users*; this WIKI captures
  *decisions and their history* for *builders*.
- **vs ADRs** — lighter: no one-file-per-decision, no formal status lifecycle. Just
  edit-the-truth + append-the-journey.
- **vs a per-run log (LAB.md)** — same two-zone shape, but scoped to one experiment
  instead of the whole project. The original repo runs both: `WIKI.md` for
  architectural / cross-run decisions, `runs/<id>/LAB.md` for per-run decisions.
