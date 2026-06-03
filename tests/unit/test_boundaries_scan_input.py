# tests/unit/test_boundaries_scan_input.py
#
# RESPONSIBILITY
#   Cover the contract of boundaries/scan_input.run.
#
# WHAT TO TEST
#   - Clean input yields ScanVerdict(blocked=False, findings=[], redacted_text=None)
#     and emits exactly ONE AuditEvent with decision="allow",
#     boundary="input_scan", finding_count=0.
#   - Text containing a high-severity PII pattern yields blocked=True,
#     non-empty findings, redacted_text populated, AuditEvent with
#     decision="blocked", max_severity="high", finding_count >= 1.
#   - enabled=False: returns an allow verdict immediately, emits one
#     AuditEvent with disabled=True, finding_count=0. NO scanners are
#     called.
#   - A scanner that raises an exception is logged and treated as
#     having returned no findings; the pipeline continues with the
#     remaining scanners; exactly one AuditEvent is still emitted.
#   - block_at threshold: a medium-severity finding does NOT block when
#     block_at="high"; the same finding DOES block when block_at="medium".
#
# INVARIANT TESTS (do not skip these)
#   - For every code path, assert that exactly one AuditEvent was emitted.
#     This is the structural rule from CLAUDE.md §6.
#   - For every emitted event, assert that adapters list contains only
#     scanners that actually ran (not skipped, not errored before
#     returning).
#
# DO NOT
#   - Mock the AuditEmitter. Use the RecordingSink from conftest.py.
#     Mocks defeat the invariant check.
