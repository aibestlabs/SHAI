# Boundary contracts

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

The canonical per-boundary specification. CLAUDE.md §3.2 has the
condensed version; this document is the full reference that adapter
authors and integrators rely on.

One section per boundary (scan_input, check_tool_call, scan_output).
Each section covers:

1. **Signature** — exact Python signature, including keyword-only args
   and defaults.
2. **Algorithm** — the numbered steps the implementation follows
   (same steps as the header comment in `boundaries/<name>.py`, but
   here they are the authoritative reference).
3. **Return type** — link to the dataclass definition; spell out what
   each field means in this boundary's context (e.g. what
   `redacted_text` means specifically for scan_input vs scan_output).
4. **Disable semantics** — what "disabled" means, what the audit event
   looks like, why this is "no silent disable."
5. **Audit event shape** — list the fields populated for this boundary
   with example values. Cross-link to `docs/audit-schema.md`.
6. **Failure modes** — adapter errors (logged, pipeline continues),
   audit emission errors (propagated), construction errors (refuse to
   start).
7. **What this boundary does NOT do** — short list to defuse common
   confusions.

## What does NOT go here

- Generic security advice. This is a reference document, not a primer.
- Code samples beyond function signatures. Examples live in `examples/`.
