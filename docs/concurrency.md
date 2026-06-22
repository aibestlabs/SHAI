# Concurrency

SHAI is designed for concurrent async use within a single process. One `Harness` instance serves many concurrent agent turns safely.

---

## View isolation

Each call to `harness.load_sources(ctx)` creates a fresh `InMemoryRegistryView` keyed by `id(ctx)`. This is Python's object identity — two distinct `RuntimeContext` objects always have distinct keys even if they represent the same logical agent.

```python
# Two concurrent turns for the same agent — isolated by object identity
ctx_a = RuntimeContext(agent_id="orchestrator_agent")
ctx_b = RuntimeContext(agent_id="orchestrator_agent")

assert id(ctx_a) != id(ctx_b)   # distinct keys → distinct views

await asyncio.gather(
    harness.load_sources(ctx_a),
    harness.load_sources(ctx_b),
)
# _views[id(ctx_a)] and _views[id(ctx_b)] are two separate objects
```

**Why `id(ctx)` and not `agent_key()`?**

`agent_key()` returns `(agent_id, sub_agent_id or "")`. Ten concurrent turns for the same agent would all share one key — last writer wins, earlier turns lose their view. `id(ctx)` gives per-object uniqueness at zero cost.

**Lifetime:** the view lives from `load_sources(ctx)` to `unload_sources(ctx)`. The caller must hold a strong reference to `ctx` for the duration of the turn — if `ctx` is garbage-collected and a new `RuntimeContext` happens to reuse the same `id()`, `check_tool_call` will not find the view and will fall back to a fresh base-registry view.

---

## Shared base registry

`InMemoryRegistry` is the shared base. Writes (`register`, `register_many`) hold a `threading.Lock`. Reads (`get`, `list`) are lock-free — GIL-safe in CPython.

**Startup invariant:** `register_tools()` must be called before any `load_sources()` call. Registering tools during a live turn is not supported and may produce inconsistent view snapshots.

---

## Audit emission

`AuditEmitter.emit()` fans out to all sinks concurrently via `asyncio.gather`. Individual sink failures are logged and swallowed. All sinks failing raises `AuditEmissionError`.

`StdoutSink` writes synchronously — stdout writes are fast enough that blocking the event loop briefly is acceptable. `FileSink` uses `asyncio.Lock` + `run_in_executor` for ordered, non-blocking file I/O.

---

## Thread safety

The harness is async-first. All boundary methods are `async def`. The `threading.Lock` in `InMemoryRegistry` exists to protect startup writes from threads (e.g. a background reload thread). The async boundaries themselves never hold the lock — they read without locking.

`scope_context_for_subagent` is the only synchronous method on the facade. It reads from the registry (lock-free) and constructs a new frozen `RuntimeContext`. It is safe to call from any thread.

---

## Parent + subagent concurrent

```python
parent_ctx = RuntimeContext(agent_id="orchestrator_agent")
child_ctx  = harness.scope_context_for_subagent(parent_ctx, "research_sub")

# Load both views concurrently
await asyncio.gather(
    harness.load_sources(parent_ctx),
    harness.load_sources(child_ctx),
)

# Run gates concurrently — each uses its own view
await asyncio.gather(
    harness.check_tool_call("search_docs", {}, parent_ctx),
    harness.check_tool_call("search_docs", {}, child_ctx),
)

# Unload
await asyncio.gather(
    harness.unload_sources(parent_ctx),
    harness.unload_sources(child_ctx),
)
```

The parent and child views are distinct objects at distinct `id()` keys. Tool additions to the child's overlay never appear in the parent's view.

---

## Hazards to avoid

**Don't reuse a RuntimeContext across turns.** Create a fresh one per turn. The `id(ctx)` key is per-object, not per-turn-semantics.

**Don't call `load_sources` twice with the same ctx without calling `unload_sources` in between.** The second call overwrites the view in `_views` — the first view is lost.

**Don't register tools after startup.** `register_tools()` acquires a threading.Lock. Calling it mid-turn may block coroutines briefly and will not update views that are already open.

**Don't hold ctx beyond the turn.** If `ctx` is held in a long-lived data structure, its `id()` may appear in `_views` indefinitely — the view is never GC'd and tools from old source activations remain visible.
