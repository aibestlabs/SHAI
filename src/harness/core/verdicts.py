# harness/core/verdicts.py — wire types returned by the three boundaries.
#
# RESPONSIBILITY
#   Define the immutable result objects the agent receives from each
#   boundary. These are PART OF THE PUBLIC API — changing their shape is
#   a breaking change for every customer.
#
# WHAT TO IMPLEMENT
#   - Finding: one match from one scanner. Frozen pydantic model. Fields:
#       scanner:   str                    (adapter name)
#       category:  str                    (e.g. "pii.email", "secret.aws_key",
#                                          "injection.prompt_override")
#       severity:  Severity               (from core.types)
#       span:      tuple[int, int] | None (start, end offsets in source text)
#       detail:    str | None             (short note; never the raw match text)
#
#   - ScanVerdict: aggregate result of scan_input or scan_output. Frozen.
#       blocked:        bool
#       findings:       list[Finding]
#       redacted_text:  str | None
#
#   - GateDecision: result of check_tool_call. Frozen.
#       allowed:        bool
#       deny_reason:    str | None        (required when allowed=False)
#       redacted_args:  dict[str, Any] | None
#
# DO NOT
#   - Include raw matched text in Finding.detail.
#   - Add mutation methods. Verdicts are produced once and consumed once.
#   - Add a VerifyResult type — verify_output is not part of core.
