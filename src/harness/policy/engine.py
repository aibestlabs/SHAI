# harness/policy/engine.py — the PolicyEngine Protocol.
#
# RESPONSIBILITY
#   Define the single Protocol every policy engine implements. The reference
#   rule-based evaluator lives in policy/rules.py. OPA and Cedar evaluators
#   live in harness-enterprise.
#
# WHAT TO IMPLEMENT
#   - PolicyEngine as a typing.Protocol:
#
#       class PolicyEngine(Protocol):
#           name: str
#
#           def evaluate(
#               self,
#               tool: Tool,
#               args: dict[str, Any],
#               ctx: RuntimeContext,
#               *,
#               rules: list[RuleConfig] | None = None,
#           ) -> PolicyDecision:
#               """Decide whether tool may be called with args under ctx.
#
#               When rules is provided (agent-scoped rules from agent-xx.yaml),
#               evaluate those first. First match → return immediately.
#               If no agent rule matches, evaluate the engine's configured
#               global rules. First match → return. No match → default allow.
#
#               This two-pass behaviour is the canonical three-layer model
#               defined in CLAUDE.md §6. The engine implements it; the
#               boundary delegates to it.
#
#               Raises PolicyEvaluationError ONLY when the policy itself
#               cannot be evaluated (bad bundle, network failure).
#               A normal deny is a PolicyDecision, not an exception.
#               """
#
#           def evaluate_source(
#               self,
#               source: ToolSource,
#               ctx: RuntimeContext,
#           ) -> SourceDecision:
#               """Decide whether source should be active for this turn.
#               Called by SourceRegistry.activate() inside load_sources().
#               Returns SourceDecision(active=True|False).
#               """
#
#   - SourceDecision: small frozen dataclass:
#       active: bool
#       reason: str | None   (why suppressed; None when active=True)
#
# DO NOT
#   - Add reload() or compile() to the Protocol.
#   - Pass the AuditEmitter into evaluate(). Audit is the boundary's job.
#   - Make the Protocol async unless the whole stack is async.
#   - Add a SandboxPolicy Protocol — it was removed. Code-execution tools
#     use tags (e.g. "code_execution") and policy rules, same as any tool.
