# harness/adapters/tool_sources/base.py — ToolSource Protocol and SourceRegistry.
#
# RESPONSIBILITY
#   Define two things that belong together:
#   1. ToolSource Protocol — what every tool source adapter implements.
#   2. SourceRegistry — the internal manager that activates sources per
#      turn, populates the ScopedRegistryView, and returns the tool list.
#      This is the implementation of Harness.load_sources().
#
# TOOLSOURCE PROTOCOL
#
#   class ToolSource(Protocol):
#       name:      str                 (entry-point name)
#       transport: Transport           (local | mcp | skill)
#       tags:      list[str]           (for policy source activation)
#
#       def load(self, ctx: RuntimeContext) -> list[Tool]:
#           """Return the tools this source provides for this context.
#           For MCP sources: connect and enumerate tools.
#           For skill sources: resolve tool group from registry.
#           For local sources: return the statically registered tools.
#           Credentials are injected at construction time — this call
#           is credential-free. Must be thread-safe.
#           """
#
# SOURCE REGISTRY
#
#   class SourceRegistry:
#       Constructor takes list[ToolSource], PolicyEngine, ToolRegistry.
#
#       activate(ctx: RuntimeContext) -> list[Tool]:
#           1. For each source declared in agent's profile (agent.sources),
#              call policy.evaluate_source(source, ctx).
#              Suppressed sources are skipped.
#           2. For active sources, call source.load(ctx).
#           3. Add loaded tools to the ScopedRegistryView for this ctx.
#           4. Return the flat list of all active tools.
#
#       The SourceRegistry never writes to the shared ToolRegistry base.
#       It always works through a ScopedRegistryView. See CLAUDE.md §6.
#
# ENTRY POINT GROUP: harness.tool_sources
#
# DO NOT
#   - Store per-turn state on SourceRegistry.
#   - Make load() async unless the whole stack is async.
#   - Add credential resolution logic to load().
#   - Add a sandbox transport — removed. Use tags on Tool instead.
