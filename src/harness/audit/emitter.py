# harness/audit/emitter.py — the AuditEmitter, fan-out to all sinks.
#
# RESPONSIBILITY
#   Receive one AuditEvent from a boundary and ship it to every
#   configured AuditSink. Single point of fan-out. This is the function
#   every boundary calls — there is no "skip audit" option.
#
# WHAT TO IMPLEMENT
#   - AuditEmitter class:
#       __init__(self, sinks: list[AuditSink])
#         - sinks may be empty in tests; in production, config.schema
#           requires at least one sink to be configured.
#
#       emit(self, event: AuditEvent) -> None
#         - For each sink, call sink.emit(event).
#         - Wrap each call in try/except. Log sink failures with the
#           canonical fields (adapter=sink.name, boundary=event.boundary,
#           tenant_id=event.tenant_id, op="audit_emit").
#         - If ALL sinks raise, raise AuditEmissionError with full
#           context. A single sink failure is recoverable; total
#           audit blackout is structural and must surface to the agent.
#
#       close(self) -> None
#         - Call close() on every sink, swallow per-sink errors.
#
#   - The emitter is NOT a queue, batcher, or async worker. It is
#     synchronous and one-event-at-a-time. Sinks that need batching
#     handle it themselves.
#
# INVARIANTS
#   - emit() must call every sink, even after one fails. The "log and
#     continue" pattern is deliberate — partial coverage is better than
#     none.
#   - The AuditEvent passed in is already redacted by the boundary (via
#     audit/redaction.py if applicable). The emitter does not redact.
#
# DO NOT
#   - Add filtering, sampling, or transformation here. Sinks transform
#     for their transport; cross-sink filtering is not a thing customers
#     ask for and would obscure the canonical fan-out.
#   - Spawn threads or async tasks. If a sink is slow, it slows the
#     boundary — that's intentional; a CISO wants the audit to land
#     before the response goes out.
#   - Re-export sinks. The emitter takes them; callers don't reach
#     through it.
