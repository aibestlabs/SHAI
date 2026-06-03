# harness/agents/agent_config.py — the AgentConfig schema.
#
# RESPONSIBILITY
#   Define the pydantic model that validates an agent-xx.yaml file.
#   This is the source of truth for what a valid agent definition looks
#   like. AgentConfig is PART OF THE PUBLIC API.
#
# WHAT TO IMPLEMENT
#   - AgentConfig as a frozen pydantic model (extra="forbid"):
#
#       id:               str              (required, non-empty, unique in registry)
#       display_name:     str | None
#       version:          str | None       (semver string; informational only)
#
#       # Layer 1 — hard capability gate
#       allowed_tags:     list[str]        (required; non-empty)
#       allowed_tool_names: list[str]      (optional; empty means all tools
#                                          within allowed_tags are accessible)
#
#       # Tool sources active for this agent
#       sources:          list[str]        (source names from harness.yaml
#                                          tool_sources; empty means no
#                                          dynamic sources — local tools only)
#
#       # Layer 2 — agent-scoped policy rules (evaluated before global rules)
#       policy_rules:     list[RuleConfig] (optional; same schema as global
#                                          rules in harness.yaml)
#
#       # Per-agent observability
#       log_level:        str = "INFO"     (DEBUG | INFO | WARNING | ERROR)
#       audit_tags:       dict[str, str]   (extra tags on every AuditEvent
#                                          for this agent)
#
#   - RuleConfig: the per-rule schema. Same structure as global policy
#     rules (see docs/policy.md). Reuse the same pydantic model from
#     policy/rules.py — do not duplicate the schema.
#
#   - Validators:
#       - allowed_tags non-empty (an agent with no tags can call nothing)
#       - id matches [a-z][a-z0-9_]* (snake_case, no spaces)
#       - log_level is one of the four valid values
#
# DO NOT
#   - Add executor, LLM client, or loop configuration. The harness does
#     not own the agent's loop.
#   - Add a sources section that duplicates harness.yaml tool_sources
#     definitions. Agent sources reference names declared in harness.yaml.
#   - Make AgentConfig mutable after construction.
