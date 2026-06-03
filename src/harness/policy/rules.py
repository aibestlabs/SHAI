# harness/policy/rules.py — the reference rule-based PolicyEngine.
#
# RESPONSIBILITY
#   Reference PolicyEngine using YAML-declared rules. Implements both
#   evaluate() (tool call gate) and evaluate_source() (source activation).
#   Usable standalone with pip install harness.
#
# WHAT TO IMPLEMENT
#   - RuleBasedPolicy implementing PolicyEngine Protocol:
#       name = "rules"
#
#       Constructor takes path to a rules YAML file OR an in-memory list
#       of rule dicts. Validates at construction; ConfigError on invalid
#       structure. Rules are NOT reloaded at runtime.
#
#   - evaluate(tool, args, ctx, *, rules=None) -> PolicyDecision:
#       Two-pass evaluation:
#         Pass 1: if rules provided (agent-scoped), evaluate in order.
#                 First match → return PolicyDecision immediately.
#         Pass 2: evaluate engine's loaded global rules in order.
#                 First match → return PolicyDecision.
#         No match → PolicyDecision(action="allow").
#
#   - evaluate_source(source, ctx) -> SourceDecision:
#       Evaluate source-activation rules from the loaded rule set.
#       Rules match on source.tags and ctx fields.
#       Default: SourceDecision(active=True).
#
#   - Rule grammar (see docs/policy.md for full spec):
#       match:
#         tool_tags:    list[str]   (any-intersection; use "code_execution"
#                                    to match code-execution tools)
#         tool_names:   list[str]
#         transport:    list[str]   (local | mcp | skill)
#         agent_ids:    list[str]
#         source_tags:  list[str]   (for evaluate_source rules only)
#         any / all / not: nested combinators
#       action: allow | deny | redact | suppress
#       reason: str                 (required for deny)
#       redact: dict                (required for redact; complete arg replacement)
#       id:     str                 (stable rule id → PolicyDecision.rule_id)
#
#   - First-match-wins. Declaration order is priority.
#
# DO NOT
#   - Add CEL, regex, or expression languages. That is OPA/Cedar territory.
#   - Reload rules at runtime.
#   - Add sandbox-specific rule types — use tool_tags: ["code_execution"].
