# harness/boundaries/scan_output.py — the scan_output boundary.
#
# RESPONSIBILITY
#   Run the configured output scanners over text the agent is about to
#   return to the user, aggregate findings, emit exactly one audit event,
#   and return a ScanVerdict. Disable-able via config.
#
# WHAT TO IMPLEMENT
#   Structurally identical to scan_input.run, with one difference:
#     - boundary name in the AuditEvent is "output_scan", not "input_scan".
#     - the scanner set is the OUTPUT scanner set (configured separately
#       from input scanners in harness.yaml).
#
#   Signature:
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
#   THREAT MODEL NOTE (for the coding agent's benefit):
#     This boundary catches a different category of issue than scan_input:
#       - LLM hallucinations of real PII (phone numbers, emails, SSNs).
#       - Tool results that leaked into the narrative response.
#       - Retrieved memory whose sensitivity tag the LLM didn't respect.
#       - Prompt-injection tails trying to exfiltrate data on the way out.
#     Output scanners are configured separately because the patterns of
#     concern differ (less "user trying to attack us", more "model
#     leaking what it shouldn't").
#
# SHARED LOGIC
#   If the implementation here is a byte-for-byte copy of scan_input.run
#   apart from the boundary name string and scanner argument, extract a
#   private helper in boundaries/__init__.py (or boundaries/_scan_pipeline.py)
#   and have both files delegate to it. Do not duplicate. See CLAUDE.md
#   §5 "Converge duplicate concepts into one canonical path."
#
# DO NOT
#   - Add a re-entry into the LLM. The agent owns retry logic, not the
#     harness.
#   - Couple this file to scan_input.py via direct import. If they share
#     logic, both import the helper from boundaries/__init__.py.
