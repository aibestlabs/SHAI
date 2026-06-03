# harness/audit/redaction.py — field-level redaction helpers.
#
# RESPONSIBILITY
#   Provide the small set of helpers boundary code uses to scrub
#   sensitive content out of values BEFORE they go into an AuditEvent.
#   AuditEvent has no raw-text field by design, but adapters surface
#   small bits of context in `extra` and those need scrubbing.
#
# WHAT TO IMPLEMENT
#   - redact_string(text: str, max_len: int = 128) -> str
#       Returns a fingerprint-style summary safe for audit:
#         - Truncate to max_len.
#         - Replace digit runs of length >= 4 with "[NUM]".
#         - Replace anything matching the common PII regex shapes
#           (email, phone, credit-card length digits) with "[REDACTED]".
#       This is COARSE deliberately — it's a defence-in-depth backstop,
#       not a replacement for the configured Scanner pipeline.
#
#   - hash_value(value: Any) -> str
#       Stable SHA-256-prefix hash for correlating events about the
#       same input without leaking the input. Use for tool args or
#       user-input fingerprints when audit consumers need to group.
#
#   - safe_extra(d: dict[str, Any]) -> dict[str, Any]
#       Recursively walk a dict, applying redact_string to all string
#       values and hash_value to any value larger than a threshold
#       (e.g. >256 bytes serialized). Used by boundaries when populating
#       AuditEvent.extra from adapter outputs.
#
# DO NOT
#   - Use these as the primary scanner pipeline. They are coarse
#     backstops. Real detection happens in Scanner adapters.
#   - Add reversible encryption. Audit redaction is one-way.
#   - Vary output by tenant. Redaction is a property of the data shape,
#     not the tenant — keeping it tenant-agnostic means a wrong
#     RuntimeContext can't downgrade redaction.
