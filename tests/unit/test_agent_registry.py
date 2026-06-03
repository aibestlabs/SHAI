# tests/unit/test_agent_registry.py
#
# RESPONSIBILITY
#   Cover agents/registry.py using the AgentRegistry directly
#   (not through the facade).
#
# WHAT TO TEST
#   - load: happy path, idempotent, conflict.
#   - reload: replaces definition, rejects invalid file, rejects unknown id.
#   - deregister: removes, raises on unknown.
#   - get: returns correct AgentConfig, raises on unknown.
#   - list: returns all registered in order.
#   - Concurrent get: 50 threads get() the same agent simultaneously —
#     no exceptions, consistent results.
#   - In-flight isolation: reload swaps definition; a RuntimeContext
#     constructed before the reload carries the old allowed_tags snapshot
#     and is unaffected by the swap.
#
# USE
#   tests/fixtures/agents/email_agent.yaml and research_agent.yaml
#   as test fixtures. Create minimal valid files.
