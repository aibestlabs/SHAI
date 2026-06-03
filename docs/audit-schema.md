# Audit event schema

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

Field-by-field documentation of `AuditEvent` (defined in
`harness/core/events.py`). This document is the contract every audit
sink ships against and every SIEM dashboard parses.

For each field:

1. **Name** — the canonical field name (matches CLAUDE.md §6 logging
   field names; matches the pydantic attribute name).
2. **Type** — Python type and JSON serialization shape.
3. **Required / optional** — and the rules tying optionality to other
   fields (e.g. `tool_name` required when `boundary == "tool_call_gate"`).
4. **Meaning** — what the field tells the audit consumer.
5. **Example values** — short concrete examples.

Plus three short sections:

- **Invariants enforced by the schema** — list the cross-field
  constraints (deny ⇒ deny_reason, etc.).
- **What is NEVER in an AuditEvent** — raw user input, raw LLM
  output, raw tool args, raw scanner matches. The reason: PII
  containment.
- **Wire format examples** — one JSON example per boundary,
  illustrating an allow, a deny, a block, and a disabled emission.

## What does NOT go here

- Sink-specific transport metadata (Splunk index, OTel trace id).
  Those are sink concerns and live in the sink's own docs.
