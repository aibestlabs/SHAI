# harness/adapters/scanners/base.py — the Scanner Protocol.
#
# RESPONSIBILITY
#   Define the single Protocol every text scanner implements. Reference
#   scanners live in this directory (regex_pii.py, basic_injection.py);
#   production scanners (Purview, Nightfall, Lakera, Forcepoint) live in
#   harness-enterprise/scanners/.
#
# WHAT TO IMPLEMENT
#   - Scanner as a typing.Protocol:
#
#       class Scanner(Protocol):
#           name: str  # adapter name, matches entry-point name
#
#           def scan(
#               self,
#               text: str,
#               ctx: RuntimeContext,
#           ) -> ScanResult:
#               """Inspect text. Return findings (possibly empty) and
#               optionally a redacted form of the input. Pure function
#               from inputs to result — no side effects, no audit
#               emission, no logging beyond errors."""
#
#   - ScanResult is a small internal type local to this module:
#       findings:       list[Finding]
#       redacted_text:  str | None
#
#     ScanResult is NOT the public ScanVerdict — the boundary aggregates
#     ScanResults from multiple scanners into one ScanVerdict.
#
# DO NOT
#   - Add a `severity_threshold` parameter. Scanners report what they
#     find; the boundary decides what to block on (see scan_input.run
#     block_at parameter).
#   - Make scan() async unless every adapter and boundary is async.
#   - Add per-scanner configuration to the Protocol. Configuration is
#     constructor-injected from harness.yaml; the runtime contract is
#     just scan(text, ctx).
