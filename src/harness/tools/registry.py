# harness/tools/registry.py — ToolRegistry Protocol and ScopedRegistryView.
#
# RESPONSIBILITY
#   Define two tightly coupled abstractions:
#   1. ToolRegistry Protocol — the shared base, written only at startup.
#   2. ScopedRegistryView — a per-turn, per-agent overlay used by
#      load_sources and check_tool_call. Never shared between agents.
#
# TOOLREGISTRY PROTOCOL
#
#   class ToolRegistry(Protocol):
#       name: str
#
#       def register(self, tool: Tool) -> None:
#           """Idempotent on identical (name, schema, tags, transport).
#           Raises ConfigError on conflicting schema for same name.
#           STARTUP ONLY — never called during a turn."""
#
#       def register_many(self, tools: Iterable[Tool]) -> None:
#           """Convenience; loops register()."""
#
#       def get(self, name: str) -> Tool:
#           """Raises ToolNotRegisteredError on miss. Thread-safe."""
#
#       def list(self) -> list[Tool]:
#           """All registered tools. CLI / debug use only."""
#
#       def scoped_view(self, ctx: RuntimeContext) -> "ScopedRegistryView":
#           """Return a fresh per-call view for this ctx. Reads fall
#           through to the shared base; writes go to an in-call overlay
#           invisible to other agents. Never store the view on the
#           registry — the caller holds it."""
#
# SCOPED REGISTRY VIEW
#
#   class ScopedRegistryView:
#       ctx: RuntimeContext
#
#       def add(self, tool: Tool) -> None:
#           """Add to the per-call overlay. Never touches shared base."""
#
#       def get(self, name: str) -> Tool:
#           """Overlay first, then shared base.
#           Raises ToolNotRegisteredError on miss."""
#
#       def list(self) -> list[Tool]:
#           """Base tools + overlay tools for this turn."""
#
#   ScopedRegistryView is INTERNAL — not exported from harness/__init__.py.
#   It is passed explicitly through the call chain from load_sources to
#   check_tool_call and discarded after the turn. It is never stored on
#   the Harness instance.
#
# DO NOT
#   - Add unregister() to the Protocol.
#   - Add policy or scanning logic here.
#   - Let ScopedRegistryView write to the shared base.
#   - Reuse a ScopedRegistryView across turns or across agents.
