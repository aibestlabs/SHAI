# harness/adapters/tool_registry/memory.py — in-process tool registry.
#
# RESPONSIBILITY
#   Reference ToolRegistry implementation backed by a plain dict.
#   Also implements ScopedRegistryView as an in-memory overlay.
#   Appropriate for single-process agents.
#
# WHAT TO IMPLEMENT
#   - InMemoryRegistry implementing ToolRegistry Protocol:
#       name = "memory"
#       Internal state: dict[str, Tool] (insertion-ordered)
#       Write lock: threading.Lock (protects register/register_many only;
#       reads are GIL-safe in CPython)
#
#       register(tool):
#         - Identical tool: no-op.
#         - Conflicting tool (same name, different content): ConfigError.
#         - New tool: store.
#
#       get(name): return tool or raise ToolNotRegisteredError.
#       list(): return tools in insertion order.
#
#       scoped_view(ctx) -> InMemoryRegistryView:
#         Return a fresh InMemoryRegistryView wrapping this registry
#         for the given ctx. Each call returns a new, empty overlay.
#
#   - InMemoryRegistryView implementing ScopedRegistryView:
#       Constructor takes (base: InMemoryRegistry, ctx: RuntimeContext).
#       Internal state: dict[str, Tool] (the per-turn overlay)
#
#       add(tool): write to overlay dict only.
#       get(name): check overlay first, then base.get(name).
#       list(): base.list() + list(overlay.values()), deduplicated by name
#               (overlay wins on conflict).
#
# CONCURRENCY
#   - register() / register_many() hold the write lock.
#   - get() and list() on the base are lock-free (GIL in CPython).
#   - InMemoryRegistryView is single-agent — no locking needed on the
#     overlay dict (one agent, one thread per turn in sync model).
#
# ENTRY POINT
#   Registered under harness.tool_registry as "memory".
