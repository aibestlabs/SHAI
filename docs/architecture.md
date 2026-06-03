# Architecture

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

The full folder tree of `src/harness/` with one-paragraph descriptions
of each module's responsibility. CLAUDE.md §3.5 has the compressed
version; this document is the long-form companion.

Sections to include:

1. **System overview** — one diagram (ASCII or mermaid) showing the
   customer agent above the Harness facade, the three boundary
   functions inside it, and the adapter Protocols at the bottom edge.
   Repeat the diagram in `README.md`-friendly form so the canonical
   picture appears in one place only.

2. **Module-by-module description** — for each subdirectory under
   `src/harness/`, a paragraph naming the module's single
   responsibility, the types it owns, and the modules it depends on.
   This document is what a new contributor reads after CLAUDE.md.

3. **Adapter discovery and the three-package layout** — explain the
   entry-point mechanism, name the canonical groups, show how
   `harness-enterprise` and third-party packages register without
   touching `harness`.

4. **Bootstrap order** — document the resolution decision made in
   `config/resolution.py` (which of the two strategies for resolving
   secrets-section secrets is in force).

5. **Build order** — repeat or link to the phases in CLAUDE.md §4 so
   this document stands alone for someone bootstrapping the repo.

## What does NOT go here

- Per-boundary behavioral contracts (those live in `docs/boundaries.md`).
- Audit event field semantics (those live in `docs/audit-schema.md`).
- Rule grammar (lives in `docs/policy.md`).
- Per-adapter how-to (lives in `docs/adapters.md`).

Keep this file purely about structure and dependencies.
