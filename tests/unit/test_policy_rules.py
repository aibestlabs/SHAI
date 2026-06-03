# tests/unit/test_policy_rules.py
#
# RESPONSIBILITY
#   Cover policy/rules.py (the reference RuleBasedPolicy).
#
# WHAT TO TEST
#   - Match by tool_tags (any-intersection semantics): a rule listing
#     ["external_write"] matches a tool tagged ["external_write", "internal"].
#   - Match by tool_names (exact membership).
#   - Match by tenants: a rule matches only when ctx.tenant_id is in
#     the list.
#   - Boolean combinators: any/all/not behave as documented.
#   - First-match-wins: a later rule that would also match does NOT
#     change the decision.
#   - Default-allow: no rule matches → PolicyDecision(action="allow").
#   - Deny rule: produces PolicyDecision(action="deny", reason=<from rule>),
#     rule_id matches the rule's id.
#   - Redact rule: produces PolicyDecision with action="redact" and
#     redacted_args = COMPLETE replacement dict (not a delta).
#   - Invalid rule structure at construction → ConfigError.
#   - A rule whose match block references unknown fields → ConfigError
#     at construction time (extra="forbid").
#
# DO NOT
#   - Test the gate's translation from PolicyDecision to GateDecision
#     here. That belongs in test_boundaries_check_tool_call.py.
