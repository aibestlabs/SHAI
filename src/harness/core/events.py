# harness/core/events.py — the AuditEvent schema.
#
# RESPONSIBILITY
#   Define the structured event every boundary emits exactly once per call.
#   Consumed by every AuditSink and seen by every customer's CISO.
#   See docs/audit-schema.md for the field-by-field spec.
#
# WHAT TO IMPLEMENT
#   - AuditEvent as a frozen pydantic model. Fields (canonical names —
#     match CLAUDE.md §6 logging field names exactly):
#       timestamp:       datetime          (UTC)
#       boundary:        BoundaryName      (input_scan | tool_call_gate | output_scan)
#       decision:        Decision          (allow | deny | redact | blocked)
#       disabled:        bool              (true when boundary disabled by config)
#       tenant_id:       str
#       agent_id:        str
#       user_id:         str | None
#       session_id:      str | None
#       request_id:      str | None
#       adapters:        list[str]         (adapter names that ran)
#       tool_name:       str | None        (tool_call_gate only)
#       transport:       str | None        (tool_call_gate only)
#       finding_count:   int
#       max_severity:    Severity | None
#       deny_reason:     str | None        (deny / blocked decisions only)
#       duration_ms:     int
#       extra:           dict[str, Any]    (small adapter-specific context)
#
#     Constraints enforced at model level:
#       - decision="deny" → deny_reason non-empty, boundary="tool_call_gate"
#       - decision="blocked" → boundary is a scan boundary
#       - disabled=True → decision="allow", finding_count=0
#       - tool_name and transport populated only for tool_call_gate
#
#   - AuditEvent.build(...) — canonical builder called by boundaries.
#     Boundaries never construct AuditEvent by hand.
#
# DO NOT
#   - Include raw user input, raw LLM output, raw tool args, or raw
#     scanner matches in any field, including extra.
#   - Add source_names — load_sources does not emit audit events.
#   - Add sink-specific transport fields (Splunk index, OTel trace id).
#   - Make AuditEvent mutable.
