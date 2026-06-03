# tests/unit/test_agent_config.py
#
# RESPONSIBILITY
#   Cover agents/agent_config.py schema validation.
#
# WHAT TO TEST
#   - Valid minimal config parses correctly.
#   - allowed_tags empty → ValidationError.
#   - id with spaces or uppercase → ValidationError.
#   - log_level invalid value → ValidationError.
#   - Extra unknown fields → ValidationError (extra="forbid").
#   - policy_rules use the same RuleConfig schema as global rules —
#     invalid rule structure raises ValidationError.
#   - sources list references names as strings — no validation against
#     harness.yaml at AgentConfig parse time (that happens at runtime
#     when load_sources resolves them).
