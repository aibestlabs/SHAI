# harness/adapters/scanners/regex_pii.py — reference PII scanner.
#
# RESPONSIBILITY
#   Detect common PII patterns using regex. Ships with the core so
#   `pip install harness` provides a usable input/output scan path
#   without external dependencies.
#
# WHAT TO IMPLEMENT
#   - RegexPIIScanner class implementing the Scanner Protocol:
#       name = "regex_pii"
#       Constructor takes an optional list of categories to enable
#       (defaults to all). Each category has a built-in pattern and
#       severity:
#         email          medium      RFC-5322-ish; common shapes only
#         phone          medium      international + US shapes
#         ssn            high        US SSN format
#         credit_card    high        Luhn-validated digit sequence
#         ipv4           low         dotted quad (low signal in most contexts)
#         api_key_like   medium      long base64/hex tokens
#
#   - scan() returns ScanResult:
#       findings: one Finding per match, populated with:
#         scanner="regex_pii", category=<above>, severity=<above>,
#         span=(start, end), detail=<short note, NEVER the matched text>
#       redacted_text: a copy of `text` with each match replaced by
#         "[REDACTED:<category>]". Stable redaction — same input always
#         yields the same output so downstream caches don't churn.
#
# DO NOT
#   - Put the matched text in Finding.detail or anywhere else the
#     result surfaces. Span offsets are enough for callers that need
#     to highlight matches in their own UI.
#   - Optimize the patterns into one mega-regex. Per-category compile is
#     readable and fast enough; one mega-regex is the kind of cleverness
#     CLAUDE.md §5 warns against.
#   - Add ML-based detection. That's what Purview / Lakera are for in
#     harness-enterprise. The reference scanner is REGEX, by design.
#
# ENTRY POINT
#   Registered under `harness.scanners` as `regex_pii` in pyproject.toml.
