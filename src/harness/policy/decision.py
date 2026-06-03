# harness/policy/decision.py — the PolicyDecision wire type.
#
# RESPONSIBILITY
#   The result type that PolicyEngine.evaluate returns. INTERNAL — not
#   re-exported from harness/__init__.py. Agents see GateDecision, not
#   this.
#
# WHAT TO IMPLEMENT
#   - PolicyDecision as a frozen pydantic model:
#       action:        Literal["allow", "deny", "redact"]
#       reason:        str | None    (required when action="deny")
#       redacted_args: dict[str, Any] | None
#                                     (required when action="redact";
#                                      must be the COMPLETE replacement
#                                      args, not a delta)
#       rule_id:       str | None    (which rule fired, for audit traceability)
#
#     Validation:
#       - action="deny" → reason is non-empty.
#       - action="redact" → redacted_args is a dict.
#       - action="allow" → reason and redacted_args are None.
#
#   - check_tool_call.run translates PolicyDecision into GateDecision:
#       allow   → GateDecision(allowed=True)
#       deny    → GateDecision(allowed=False, deny_reason=reason)
#       redact  → GateDecision(allowed=True, redacted_args=redacted_args)
#     The mapping is one-way and lives in the gate, not here.
#
# DO NOT
#   - Make this type public.
#   - Add a fourth action. allow/deny/redact covers every real case.
#   - Add per-engine fields (OPA-specific data, Cedar-specific data) here.
#     If an engine needs to surface diagnostics, it goes in rule_id or
#     in the engine's own logs.
