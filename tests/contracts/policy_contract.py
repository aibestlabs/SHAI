# tests/contracts/policy_contract.py
#
# RESPONSIBILITY
#   Conformance suite every PolicyEngine adapter must pass.
#
# WHAT TO IMPLEMENT
#   - class PolicyEngineContract:
#       engine_factory: ClassVar[Callable[[], PolicyEngine]]
#
#       (Adapter authors provide an engine configured to:
#         - allow tool "always_allow" for any args/ctx
#         - deny tool "always_deny" with reason "test-deny"
#         - redact field "secret" in args of tool "redact_field" to "***"
#       The contract tests rely on these three named tools.)
#
#       def test_allow_returns_allow_action(self): ...
#       def test_deny_returns_deny_with_reason(self): ...
#       def test_redact_returns_complete_replacement_args(self): ...
#       def test_unknown_tool_does_not_crash(self):
#         The engine is permitted to allow, deny, or have a default
#         policy for unknown tools — but it MUST NOT raise an unhandled
#         exception. PolicyEvaluationError is reserved for engine
#         failures (bad bundle, network).
#       def test_pure_for_same_input(self):
#         Same (tool, args, ctx) → same PolicyDecision across calls.
#
# DO NOT
#   - Test specific rule grammar here. That's engine-specific.
