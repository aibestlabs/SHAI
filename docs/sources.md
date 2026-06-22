# Tool Sources

A tool source activates a set of tools for one agent/subagent turn. Sources are declared in `agent-xx.yaml` and activated by `harness.load_sources(ctx)` at turn start.

---

## Lifecycle

```
harness.load_sources(ctx)
  └── SourceRegistry.activate(ctx, source_names, view)
        ├── PolicyEngine.evaluate_source(source, ctx)  ← suppress check
        ├── source.load(ctx)                            ← parallel
        └── view.add(tool)                             ← overlay only
```

```
harness.unload_sources(ctx)
  └── _views.pop(id(ctx))    ← ScopedRegistryView discarded
```

The `ScopedRegistryView` (keyed by `id(ctx)`) lives for exactly one turn. Overlay tools are never written to the shared base registry.

---

## Reference sources

### LocalSource (`transport: local`)

Serves tools registered via `harness.register_tools()` at startup. For subagent calls (`ctx.allowed_tags is not None`), only tools whose tags are fully within `allowed_tags` are returned — subagents cannot see tools they have no capability for.

### SkillSource (`transport: skill`)

A named group of tools. Declared in `harness.yaml` under `tool_sources`:

```yaml
tool_sources:
  - name: docs_skill
    transport: skill
    tools: [search_docs, fetch_doc]
    tags: [skill, read, internal]
```

Each tool is resolved from the shared `InMemoryRegistry` at turn start. Missing tools are logged and skipped — not an error. Subagent tag filtering applies identically to `LocalSource`.

---

## Declaring sources in agent config

```yaml
sources:
  - docs_skill      # activates SkillSource named "docs_skill"
  - outlook_mcp     # activates an MCP source (harness-enterprise)
```

Sources not found in the `SourceRegistry` are logged and skipped, not an error.

---

## Policy-based source suppression

`PolicyEngine.evaluate_source(source, ctx)` is called for every source before loading. A `suppress` rule suppresses the source for this turn:

```yaml
# In config/policies/rules.yaml
- id: suppress_mcp_in_prod
  match:
    source_tags: [mcp]
    agent_ids: [untrusted_agent]
  action: suppress
  reason: "MCP not permitted for untrusted agents"
```

Suppressed sources produce no tools and no audit event — suppression is logged at DEBUG level only.

---

## MCP sources (harness-enterprise)

MCP sources are not in core. They connect to external tool servers via the Model Context Protocol. When configured, the `SourceRegistry` holds an `MCPSource` adapter that:

1. Connects to the MCP server URL with resolved credentials.
2. Lists available tools and maps them to `Tool` objects.
3. Adds them to the `ScopedRegistryView` for the turn.

MCP tool calls are gated identically to local calls through `check_tool_call`. The `transport` field on the `Tool` object is `Transport.MCP`, which enables transport-based policy rules.

---

## Writing a new ToolSource adapter

```python
class MySource:
    name      = "my_source"
    transport = Transport.LOCAL
    tags: list[str] = ["my_tag"]

    async def load(self, ctx: RuntimeContext) -> list[Tool]:
        # Return tools available for this agent/subagent/turn
        ...
```

Register in `pyproject.toml`:

```toml
[project.entry-points."harness.tool_sources"]
my_source = "my_package.sources:MySource"
```

Reference in `harness.yaml`:

```yaml
tool_sources:
  - name: my_source_instance
    transport: local
    tags: [my_tag]
```
