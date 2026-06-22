# Agents

An agent is a named identity with a declared capability set. Every boundary call carries a `RuntimeContext` that identifies which agent (and optionally which subagent) is making the call.

---

## agent-xx.yaml schema

```yaml
id: orchestrator_agent          # snake_case, unique within this harness
display_name: "Orchestrator"    # optional, human-readable
version: "1.0.0"                # optional

# Capability declarations — mandatory
allowed_tool_names:
  - search_docs
  - send_email
  - list_inbox

allowed_tags:
  - read
  - internal
  - external_write

# Source activation — which tool sources to load at turn start
sources:
  - docs_skill
  - outlook_mcp

# Agent-scoped policy rules (evaluated before global rules)
policy_rules:
  - id: deny_external_write_default
    match:
      tool_tags: [external_write]
    action: deny
    reason: "external_write requires explicit permission"
  - id: allow_email_tools
    match:
      tool_names: [send_email, list_inbox]
    action: allow

log_level: DEBUG                # DEBUG | INFO | WARNING | ERROR
audit_tags:
  team: platform
  env: prod

# Subagents declared inside the parent
sub_agents:
  - id: research_sub
    allowed_tool_names: [search_docs]   # ⊆ parent allowed_tool_names
    allowed_tags: [read, internal]      # ⊆ parent allowed_tags
    sources: [docs_skill]
    policy_rules:
      - id: research_deny_write
        match:
          tool_tags: [external_write]
        action: deny
        reason: "research_sub is read-only"
```

---

## Cross-field invariants enforced at load time

These are checked at `harness.load_agent()` — not at gate time.

- `id` must match `^[a-z][a-z0-9_]*$`
- `allowed_tool_names` and `allowed_tags` must be non-empty
- Subagent `allowed_tool_names` ⊆ parent `allowed_tool_names`
- Subagent `allowed_tags` ⊆ parent `allowed_tags`
- Subagent `id` values must be unique within the parent
- `deny` rules require `reason`
- `redact` rules require `redact` dict

Violations raise `ConfigError` with the field path.

---

## Subagent model

```
orchestrator_agent
├── research_sub   (read-only)
└── email_sub      (read + external_write)
```

One parent → many subagents. One subagent → one parent. A subagent never has its own subagents.

When `scope_context_for_subagent` is called, the harness:

1. Looks up the parent `AgentConfig` by `ctx.agent_id`.
2. Finds the `SubAgentConfig` with the matching `sub_agent_id`.
3. Returns a new `RuntimeContext` with `sub_agent_id` set and `allowed_tags` narrowed to the subagent's declared tags.

The returned `RuntimeContext` carries both `agent_id` (parent identity) and `sub_agent_id` (subagent identity). Both are stamped on every `AuditEvent`.

```python
parent_ctx = RuntimeContext(agent_id="orchestrator_agent")
child_ctx  = harness.scope_context_for_subagent(parent_ctx, "research_sub")
# child_ctx.agent_id     == "orchestrator_agent"
# child_ctx.sub_agent_id == "research_sub"
# child_ctx.allowed_tags == ["read", "internal"]
```

---

## Registry lifecycle

```python
# Startup
await harness.load_agent("config/agents/orchestrator_agent.yaml")

# Runtime update (atomic swap)
await harness.reload_agent("config/agents/orchestrator_agent.yaml")

# Shutdown / test cleanup
await harness.deregister_agent("orchestrator_agent")

# Inspection
agents = await harness.list_agents()
```

`get()` (called on the hot path by boundaries) is synchronous and lock-free. Writes (`load`, `reload`, `deregister`) hold a `threading.Lock` for the duration of the dict mutation.

---

## audit_tags

`audit_tags` on `AgentConfig` are stamped on every `AuditEvent` emitted during that agent's turns. Use them to correlate events with team, environment, cost centre, or any other dimension relevant to your SIEM queries.

```yaml
audit_tags:
  team: platform
  env: prod
  user_id: "{{resolved at runtime via operator code}}"
```

`user_id` correlation: the harness does not carry `user_id`. Operators who need user-level audit correlation set `audit_tags: {user_id: <value>}` dynamically on `AgentConfig` before loading, or use a wrapper that stamps it on `extra` in the `AuditEvent`.
