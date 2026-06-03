# tests/unit/test_audit.py
#
# RESPONSIBILITY
#   Cover audit/emitter.py, audit/sink.py (the recording sink as test
#   substrate), and audit/redaction.py.
#
# WHAT TO TEST
#   - AuditEmitter.emit calls every sink. Order matches construction.
#   - A sink that raises does NOT prevent subsequent sinks from
#     receiving the event.
#   - When ALL sinks raise, AuditEmissionError is raised with all sink
#     names in its message.
#   - emitter.close() closes every sink, even when one raises during
#     close.
#   - redact_string scrubs digits and common PII shapes without
#     leaving raw matches.
#   - hash_value is stable across calls and not reversible.
#   - safe_extra walks nested dicts, redacts strings, hashes oversized
#     values.
#
# DO NOT
#   - Mock the AuditEvent schema. Construct real AuditEvent instances —
#     part of what these tests exercise is the schema's validators.
