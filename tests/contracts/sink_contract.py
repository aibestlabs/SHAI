# tests/contracts/sink_contract.py
#
# RESPONSIBILITY
#   Conformance suite every AuditSink adapter must pass.
#
# WHAT TO IMPLEMENT
#   - class AuditSinkContract:
#       sink_factory: ClassVar[Callable[[], AuditSink]]
#       (Factory returns a fresh sink instance for each test.)
#
#       def test_emit_accepts_real_audit_event(self):
#         Construct a real AuditEvent and call emit. Must not raise on
#         a well-formed event.
#       def test_name_is_stable(self): ...
#       def test_close_is_idempotent(self):
#         Calling close twice in a row does not raise.
#       def test_emit_after_close_is_an_error_or_noop(self):
#         Either behavior is acceptable, but the sink MUST NOT silently
#         pretend it shipped the event when it didn't.
#
# DO NOT
#   - Assert on the wire format. Each sink chooses its own format
#     (JSONL for stdout/file, OTel for otel, etc.). The contract is
#     behavioral, not formatic.
