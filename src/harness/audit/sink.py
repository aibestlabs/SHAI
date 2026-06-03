# harness/audit/sink.py — the AuditSink Protocol.
#
# RESPONSIBILITY
#   Define the single Protocol every audit sink implements. Reference
#   sinks (stdout JSONL, rotating file) live under adapters/audit_sinks/;
#   production sinks (Splunk, Sentinel, Elastic, OTel, S3+WORM) live in
#   harness-enterprise.
#
# WHAT TO IMPLEMENT
#   - AuditSink as a typing.Protocol:
#
#       class AuditSink(Protocol):
#           name: str  # adapter name (e.g. "stdout", "file", "splunk")
#
#           def emit(self, event: AuditEvent) -> None:
#               """Ship one event. Best-effort: a sink failure must not
#               break the boundary call. The AuditEmitter logs failures
#               and continues to the next sink. Sinks that need
#               batching, retry, or backpressure handle it internally.
#               """
#
#           def close(self) -> None:
#               """Flush and release resources. Called on process
#               shutdown. Default no-op for stateless sinks."""
#
#   - The Protocol is intentionally tiny. Sinks that need richer
#     functionality (filtering, sampling, transformation) wrap themselves
#     around this — they don't widen the interface.
#
# DO NOT
#   - Add a `flush()` method separate from close(). One way to drain.
#   - Make emit() return a status. Best-effort means best-effort; the
#     emitter logs failures via the standard logger, not the return
#     value.
#   - Add an async variant unless ALL adapters become async.
