# Policy

SHAI uses an intersection model: agent-scoped rules are evaluated first, then global rules. First deny anywhere wins. Default allow on no match.

---

## Rule grammar

```yaml
- id: my_rule            # snake_case, unique within the rule set
  match:                 # all declared conditions must be satisfied
    tool_names: []       # tool.name must be in this list
    tool_tags:  []       # tool.tags must intersect this list
    transport:  []       # tool.transport must be in this list (local|mcp|skill)
    agent_ids:  []       # ctx.agent_id must be in this list
    sub_agent_ids: []    # ctx.sub_agent_id must be in this list
    source_tags: []      # source.tags must intersect (for evaluate_source only)
    any: []              # OR combinator — any sub-match satisfies
    all: []              # AND combinator — all sub-matches must satisfy
    not: {}              # NOT combinator — sub-match must not satisfy
  action: deny           # allow | deny | redact | suppress
  reason: "why"          # required for deny
  redact:                # required for redact
    field_name: "***"
```

All `match` conditions are optional. An empty `match` matches everything.

---

## Intersection model

```
Turn: agent_id=orchestrator_agent, sub_agent_id=research_sub

Pass 1: subagent rules (research_sub.policy_rules) + parent rules (orchestrator_agent.policy_rules)
Pass 2: global rules (config/policies/rules.yaml, loaded by RuleBasedPolicy)

First deny in pass 1 OR pass 2 → GateDecision(allowed=False)
First allow in pass 1 → GateDecision(allowed=True) immediately
No match in either pass → default allow
```

**Important:** an `allow` rule in pass 1 (agent rules) returns immediately before pass 2 (global rules). To enforce a global deny that cannot be overridden by agent rules, ensure the deny rule fires in pass 2 (global), and that no agent-level allow can fire first. Use `agent_ids` in the global rule to scope it if needed.

---

## Rule evaluation

Rules are evaluated in declaration order within each list. Put more-specific rules before less-specific ones.

```yaml
policy_rules:
  # More specific first
  - id: allow_search
    match:
      tool_names: [search_docs]
    action: allow

  # Less specific catch-all
  - id: deny_all_external
    match:
      tool_tags: [external_write]
    action: deny
    reason: "external writes not permitted by default"
```

---

## Source suppression

`action: suppress` is only meaningful in `evaluate_source()`. It prevents a tool source from activating for a given agent/turn combination.

```yaml
- id: suppress_mcp_for_unvetted
  match:
    source_tags: [mcp]
    agent_ids: [unvetted_agent]
  action: suppress
  reason: "MCP not permitted for unvetted agents"
```

---

## Loading rules

### From agent-xx.yaml (agent-scoped)

```yaml
policy_rules:
  - id: my_rule
    match: {tool_tags: [external_write]}
    action: deny
    reason: "not allowed"
```

### From rules.yaml (global)

```yaml
# config/policies/rules.yaml
- id: global_deny_mcp
  match:
    transport: [mcp]
  action: deny
  reason: "MCP requires enterprise subscription"
```

Referenced in `harness.yaml`:

```yaml
policy:
  name: rules
  config:
    rules_path: ./config/policies/rules.yaml
```

---

## Writing a production PolicyEngine (harness-enterprise)

For OPA or Cedar in `harness-enterprise`, implement the `PolicyEngine` Protocol:

```python
class OPAPolicy:
    name = "opa"

    async def evaluate(self, tool, args, ctx, *, rules=None) -> PolicyDecision:
        # Call OPA REST API
        ...

    async def evaluate_source(self, source, ctx) -> SourceDecision:
        ...
```

Register under `harness.policy` entry point and reference by name in `harness.yaml`.

---

## Combinators

```yaml
# OR: deny if tool is external_write OR sensitive
- id: deny_risky
  match:
    any:
      - tool_tags: [external_write]
      - tool_tags: [sensitive]
  action: deny
  reason: "risky tool"

# AND: deny only if BOTH external_write AND mcp
- id: deny_external_mcp
  match:
    all:
      - tool_tags: [external_write]
      - transport: [mcp]
  action: deny
  reason: "external MCP not permitted"

# NOT: allow everything except external_write
- id: allow_non_external
  match:
    not:
      tool_tags: [external_write]
  action: allow
```
