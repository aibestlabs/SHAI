# tests/unit/test_boundaries_check_tool_call.py
#
# RESPONSIBILITY
#   Cover the contract of boundaries/check_tool_call.run.
#
# WHAT TO TEST
#   - Unknown tool: returns GateDecision(allowed=False,
#     deny_reason starts with "unknown tool"); AuditEvent emitted with
#     decision="deny", tool_name set.
#   - Policy allow + no arg scanning: returns allowed=True, no
#     redacted_args; AuditEvent decision="allow".
#   - Policy deny: returns allowed=False with the policy's reason;
#     AuditEvent decision="deny", deny_reason matches.
#   - Policy redact: returns allowed=True with redacted_args set to the
#     policy's replacement dict; AuditEvent decision="redact".
#   - Arg scanning triggered by tag intersection (tool tagged
#     "sensitive", scan_args_for_tags={"sensitive"}, scanner reports
#     high severity): returns deny with reason mentioning args scan;
#     AuditEvent has finding_count >= 1 and decision="deny".
#   - Arg scanner error tolerated: same behavior as scan boundaries —
#     log and continue, exactly one AuditEvent.
#   - PolicyEvaluationError propagates (not a normal deny). Audit event
#     captures the failure before re-raise.
#
# INVARIANT TESTS
#   - Exactly one AuditEvent per call, every path.
#   - On allowed=False, deny_reason is always non-empty.
#   - On allowed=True with redacted_args, the redacted_args originate
#     from policy (NOT from the arg scanner — scanners detect, they
#     don't rewrite).
#
# DO NOT
#   - Assert that any tool was executed. The gate never executes.
#   - Use real OPA or external policy engines. The reference
#     RuleBasedPolicy is the test substrate.
