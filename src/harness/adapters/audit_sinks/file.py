# harness/adapters/audit_sinks/file.py — rotating file audit sink.
#
# RESPONSIBILITY
#   Write one JSON object per line to a file on disk, rotating by size.
#   Suitable for single-host deployments and as a defence-in-depth sink
#   alongside a remote sink (Splunk, Sentinel) so audit isn't lost on
#   network failure.
#
# WHAT TO IMPLEMENT
#   - FileSink class implementing AuditSink:
#       name = "file"
#       Constructor parameters (all from harness.yaml):
#         path:           str                 (file path, required)
#         max_bytes:      int = 100_000_000   (rotate at ~100MB by default)
#         backup_count:   int = 10
#         encoding:       str = "utf-8"
#
#       Implementation uses logging.handlers.RotatingFileHandler under
#       the hood, OR a hand-written rotator if the stdlib handler's
#       behavior doesn't match (e.g. we want atomic rename, no logging
#       framework overhead). Pick one approach and stick to it.
#
#       emit(event):
#         - Serialize to JSON (one line, no pretty-print).
#         - Write + flush.
#         - On IOError, propagate to the emitter.
#
#       close():
#         - Flush + close the file handle.
#
# DO NOT
#   - Add gzip / compression. The CLI's `audit replay` reads plain JSONL;
#     compression is for downstream archival, not the live sink.
#   - Use the logging module's logger NAME for routing. This is a sink,
#     not a logger — it owns its file directly.
#   - Buffer asynchronously. Per-event flush is the contract.
#
# ENTRY POINT
#   Registered under `harness.audit_sinks` as `file`.
