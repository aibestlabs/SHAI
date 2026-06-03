# harness/adapters/audit_sinks/stdout.py — JSONL stdout audit sink.
#
# RESPONSIBILITY
#   Emit one JSON object per line to stdout. Useful in dev, in containers
#   that forward stdout to a log aggregator, and as the default sink
#   when nothing else is configured.
#
# WHAT TO IMPLEMENT
#   - StdoutSink class implementing AuditSink:
#       name = "stdout"
#       Constructor takes no required arguments. Optional `stream`
#       parameter for tests (default sys.stdout).
#
#       emit(event):
#         - Serialize event via event.model_dump_json() (pydantic v2)
#           or equivalent. The output is ONE LINE — no pretty printing.
#         - Write line + "\n" to the configured stream.
#         - Flush after each write. Audit data is not buffered.
#         - Exceptions propagate to the emitter, which logs and continues
#           to other sinks.
#
#       close(): no-op.
#
# DO NOT
#   - Add timestamps independent of event.timestamp. The event carries
#     its own.
#   - Pretty-print or color the output. This sink is structured data,
#     not human-readable display. (For the CLI's `harness audit tail`,
#     formatting happens in harness-cli, not here.)
#   - Buffer or batch. Audit is per-event.
#
# ENTRY POINT
#   Registered under `harness.audit_sinks` as `stdout`.
