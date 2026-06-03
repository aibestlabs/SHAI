# Agent registry and profiles

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

The complete reference for declaring, registering, and managing agents.

Sections:

1. **agent-xx.yaml schema** — field-by-field documentation of AgentConfig.
   Every field, its type, its default, what it does, what it doesn't do.

2. **The three-layer evaluation model** — how allowed_tags (Layer 1),
   agent-scoped policy rules (Layer 2), and global policy rules (Layer 3)
   combine inside check_tool_call. Show the evaluation flowchart.
   Make clear that Layer 1 is pre-policy and cannot be overridden by rules.

3. **Registry lifecycle** — how to load, reload, deregister, and list agents
   via the facade and via the CLI. Document the atomicity guarantee on reload:
   invalid file keeps old definition, in-flight calls complete normally.

4. **Per-agent isolation** — what each agent gets: its own RuntimeContext,
   its own ScopedRegistryView, its own audit trail, its own log_level.
   Explain that this isolation is structural, not configurable.

5. **Agent-scoped policy rules** — grammar reference for the policy_rules
   block in agent-xx.yaml. Cross-reference to docs/policy.md for the
   full rule grammar. Note that agent rules are evaluated before global
   rules and cannot escalate past Layer 1 capability tags.

6. **audit_tags** — how extra tags appear in every AuditEvent for this
   agent. Useful for per-team or per-environment filtering in SIEM.

## What does NOT go here

- The full policy rule grammar (lives in docs/policy.md).
- Source activation details (lives in docs/sources.md).
- How to write a new adapter (lives in docs/adapters.md).
