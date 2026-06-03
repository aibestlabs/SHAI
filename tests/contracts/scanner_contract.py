# tests/contracts/scanner_contract.py
#
# RESPONSIBILITY
#   The conformance suite every Scanner adapter must pass. Implemented
#   as a base test class adapter authors subclass with a single class
#   attribute: `scanner_factory`.
#
# WHAT TO IMPLEMENT
#   - class ScannerContract:
#       scanner_factory: ClassVar[Callable[[], Scanner]]
#
#       def test_returns_scanresult_shape(self):
#         scan("") returns an object with .findings (list) and
#         .redacted_text (str | None). Empty input → empty findings.
#
#       def test_findings_have_required_fields(self):
#         For non-trivial input, every Finding has non-empty scanner,
#         non-empty category, a Severity value, span is None or a
#         non-negative (start, end) tuple where end > start, detail is
#         None or a string without obvious raw-match leakage.
#
#       def test_name_is_stable(self):
#         self.scanner_factory().name equals what the entry point
#         registers it as.
#
#       def test_pure_for_same_input(self):
#         Calling scan twice with the same input returns equivalent
#         findings (allow ordering normalization).
#
#       def test_does_not_raise_on_arbitrary_text(self):
#         Pass a small property-based generator of unicode strings;
#         no scanner may crash on benign input.
#
#       def test_no_raw_match_in_finding_detail(self):
#         For a fixed PII-like input ("contact me at foo@example.com"),
#         no Finding.detail contains "foo@example.com". The category
#         is what surfaces; the raw match stays out of audit.
#
# HOW ADAPTER AUTHORS USE IT
#   # tests/unit/test_regex_pii.py
#   from tests.contracts.scanner_contract import ScannerContract
#   from harness.adapters.scanners.regex_pii import RegexPIIScanner
#
#   class TestRegexPII(ScannerContract):
#       scanner_factory = staticmethod(lambda: RegexPIIScanner())
#
#   Inheritance is the entire registration.
#
# DO NOT
#   - Test specific PII categories here (those are regex_pii-specific).
#     The contract is the shape and invariants, not the catalog.
