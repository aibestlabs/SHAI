# harness/boundaries/scan_input.py — the scan_input boundary.
#
# RESPONSIBILITY
#   Run the configured input scanners over user-provided text, aggregate
#   their findings, emit exactly one audit event, and return a
#   ScanVerdict. Disable-able via config.
#
# WHAT TO IMPLEMENT
#   - One public function:
#       def run(
#           text: str,
#           ctx: RuntimeContext,
#           *,
#           scanners: list[Scanner],
#           emitter: AuditEmitter,
#           enabled: bool,
#           block_at: Severity = Severity.high,
#       ) -> ScanVerdict
#
#   - Algorithm:
#       1. Start timer for duration_ms.
#       2. If enabled is False:
#            - Build and emit an AuditEvent with disabled=True,
#              decision=allow, finding_count=0.
#            - Return ScanVerdict(blocked=False, findings=[], redacted_text=None).
#            - This is the "no silent disable" rule (CLAUDE.md §6).
#       3. Otherwise: call each scanner in order, collect Findings.
#            - A scanner that raises is logged with full context but does
#              NOT abort the pipeline. Treat its findings as empty for
#              this call. (See CLAUDE.md §5 "Error handling" — fail
#              clearly but don't break the boundary contract.)
#            - Aggregate findings preserving order.
#       4. blocked = any(f.severity >= block_at for f in findings).
#            - block_at default is Severity.high. Configurable per
#              boundary via harness.yaml.
#       5. redacted_text = the LAST scanner's redacted output if any
#            scanner produced one; None otherwise. Scanners cooperate by
#            redacting in place.
#       6. Build AuditEvent (boundary="input_scan", decision="blocked"
#            if blocked else "allow", adapters=[s.name for s in scanners
#            that ran], finding_count, max_severity, duration_ms).
#       7. emitter.emit(event).
#       8. Return ScanVerdict.
#
# INVARIANTS
#   - Exactly one AuditEvent emitted per call, no matter what. This is
#     the structural rule from CLAUDE.md §6. Tests assert this.
#   - The function is total: it always returns a ScanVerdict. Scanner
#     errors degrade gracefully; only AuditEmissionError (all sinks
#     down) propagates.
#   - No raw text in the audit event. Pass only counts and severities
#     into AuditEvent.build.
#
# DO NOT
#   - Make decisions other than "block at severity". Anything more
#     nuanced (which categories to block, per-tenant overrides) is
#     PolicyEngine's job, not the scan boundary's.
#   - Mutate the input text. Return redacted_text on the verdict; the
#     agent decides whether to use it.
#   - Call any LLM, retrieval, or memory code from here.
