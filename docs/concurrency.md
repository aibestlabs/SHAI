# Concurrency model

This document is the authoritative reference for how a single `Harness`
instance handles multiple concurrent agents. Read it before implementing
`ToolRegistry.scoped_view`, `AuditSink.emit`, `load_sources`, or any
code that touches shared state during a boundary call.

---

## 1. The core guarantee

**One `Harness` instance safely serves any number of concurrent agents.**

The harness achieves this because boundary functions are stateless per
call — they take inputs, call adapter methods, and return outputs. No
mutable state is written to the `Harness` instance or its adapters
during a boundary call. Everything that varies per agent lives in
`RuntimeContext`, which is caller-owned and never mutated by the harness.

```
Harness instance (shared, one per deployment)
│
├── Adapters (read-only after construction)
│   ├── list[Scanner]         stateless; safe for concurrent calls
│   ├── PolicyEngine          stateless evaluator; safe for concurrent calls
│   ├── SandboxPolicy         stateless evaluator; safe for concurrent calls
│   ├── AuditEmitter          fan-out to sinks; thread-safety per sink
│   ├── ToolRegistry          reads concurrent-safe; writes startup-only
│   ├── list[ToolSource]      stateless loaders; credentials held as attrs
│   └── SecretsProvider       read-only after construction; safe
│
└── Per-call (created fresh, never shared between agents)
    ├── RuntimeContext        caller-owned identity envelope
    ├── ScopedRegistryView    per-turn view over ToolRegistry (see §3)
    └── AuditEvent            constructed and emitted per boundary call
```

---

## 2. Multi-agent deployment shapes

### 2a. Multi-tenant: many independent agents sharing one instance

The most common production shape. A single `Harness` instance serves
agents across multiple tenants. Tenant isolation is enforced entirely
through `RuntimeContext`:

- `PolicyEngine` rules match on `ctx.tenant_id` — different tenants
  get different policy decisions from the same rule set.
- `AuditEvent` carries `tenant_id` — every emitted event is tagged.
- `ScopedRegistryView` (§3) ensures that MCP tools loaded for tenant
  T1 are never visible to tenant T2's `check_tool_call`.

No per-tenant `Harness` instance is needed. No per-tenant adapter
instantiation is needed. The `RuntimeContext` is the isolation boundary.

### 2b. Subagent fan-out: a parent spawning N children concurrently

A parent agent calls `scope_context_for_subagent(parent_ctx, allowed_tags)`
once per child before fanning out. Each child receives a narrowed
`RuntimeContext` with:

- `parent_agent_id` set to the parent's `agent_id`
- `allowed_tags` restricted to a subset of the parent's tags

Each child then makes independent boundary calls through the same
shared `Harness` instance. Their calls run concurrently with no
coordination required — the shared state they touch (adapters,
base registry) is read-only.

```python
# Parent fanning out to 10 children (async example)
child_ctxs = [
    harness.scope_context_for_subagent(parent_ctx, allowed_tags=["read"])
    for _ in range(10)
]
results = await asyncio.gather(*[
    run_child_agent(harness, child_ctx) for child_ctx in child_ctxs
])
```

The parent's Harness instance handles all 10 concurrent boundary call
streams without any locking at the boundary level.

---

## 3. The scoped registry view — the critical concurrency invariant

### The problem

`load_sources` loads tools from MCP servers and skills into the tool
registry so they're available to `check_tool_call` during this turn.
If these tools were written directly into the shared `ToolRegistry`,
Agent A's Slack MCP tools would become visible to Agent B's
`check_tool_call` — a cross-tenant tool leakage bug that policy
cannot catch (policy runs after registry lookup).

### The solution: `ScopedRegistryView`

`ToolRegistry` exposes a `scoped_view(ctx) -> ScopedRegistryView`
method. The scoped view:

- **Reads** from the shared base registry (local tools registered at
  startup via `register_tools()`).
- **Writes** to a per-call, per-agent overlay dict.
- **Looks up** a tool name by checking the overlay first, then the
  base.
- **Is discarded** at the end of the turn when `unload_sources` is
  called — there is no eviction step that could race; the view ceases
  to exist.

```
Shared ToolRegistry (base, read-only at runtime)
    search_docs    → Tool(transport=local, tags=[read, internal])
    send_email     → Tool(transport=local, tags=[external_write])

Agent A's ScopedRegistryView (call overlay for this turn)
    slack_list_channels  → Tool(transport=mcp, tags=[external_read])
    slack_post_message   → Tool(transport=mcp, tags=[external_write])

Agent B's ScopedRegistryView (call overlay for this turn, simultaneous)
    browser_navigate     → Tool(transport=mcp, tags=[external_read])
    browser_screenshot   → Tool(transport=mcp, tags=[external_read])
```

Agent A's `check_tool_call("slack_list_channels", ...)` looks up the
name in A's overlay — found. Agent B's `check_tool_call("slack_list_channels", ...)`
looks up the name in B's overlay — not found → deny with "unknown tool".
The tools never cross.

### Protocol shape

```python
class ToolRegistry(Protocol):
    # ... existing methods ...

    def scoped_view(self, ctx: RuntimeContext) -> "ScopedRegistryView":
        """Return a per-call view over this registry.
        Reads fall through to the shared base; writes go to an
        in-call overlay invisible to other agents. The view is
        not stored on the registry — the caller holds it and
        passes it through the call chain.
        """

class ScopedRegistryView(Protocol):
    ctx: RuntimeContext

    def add(self, tool: Tool) -> None:
        """Add a tool to the per-call overlay."""

    def get(self, name: str) -> Tool:
        """Overlay first, then base. Raises ToolNotRegisteredError on miss."""

    def list(self) -> list[Tool]:
        """Base tools + overlay tools for this turn."""
```

### How the facade passes the view

The scoped view is created at the start of `load_sources` and passed
explicitly through to `check_tool_call` for the same turn. It is never
stored on the `Harness` instance.

```python
# core/harness.py — simplified call flow
def load_sources(self, ctx):
    view = self._tool_registry.scoped_view(ctx)
    active = self._source_registry.activate(ctx, self._policy)
    for source in active:
        tools = source.load(ctx)
        for tool in tools:
            view.add(tool)
    return view          # caller holds the view for this turn

def check_tool_call(self, name, args, ctx, *, registry_view=None):
    reg = registry_view or self._tool_registry
    tool = reg.get(name)   # raises ToolNotRegisteredError on miss → deny
    ...
```

The agent passes the view from `load_sources` to `check_tool_call`:

```python
# Agent code — hand-rolled loop
view    = harness.load_sources(ctx)
verdict = harness.scan_input(text, ctx)
gate    = harness.check_tool_call(name, args, ctx, registry_view=view)
verdict = harness.scan_output(text, ctx)
harness.unload_sources(ctx, view)
```

---

## 4. AuditSink thread-safety specification

Every `AuditSink` implementation must be safe to call from multiple
threads simultaneously. This is a Protocol-level contract, enforced by
the concurrent-emit test in `tests/contracts/sink_contract.py`.

### Contract test

```python
# tests/contracts/sink_contract.py (excerpt)
def test_concurrent_emit(self):
    """50 threads emit simultaneously. No loss, no exceptions."""
    sink = self.sink_factory()
    events = [make_audit_event() for _ in range(50)]
    errors = []

    def emit_one(e):
        try:
            sink.emit(e)
        except Exception as ex:
            errors.append(ex)

    threads = [threading.Thread(target=emit_one, args=(e,)) for e in events]
    for t in threads: t.start()
    for t in threads: t.join()

    assert not errors, f"Concurrent emit raised: {errors}"
    # Sink-specific assertion: check all 50 events were received
    # (RecordingSink: assert len(sink.events) == 50)
```

### Per-sink requirements

**`StdoutSink`**
Python's GIL makes individual `sys.stdout.write()` calls atomic in
CPython. `StdoutSink` does not add a lock. It documents this reliance
on the GIL and states clearly: do not use `StdoutSink` as the sole
production sink in a multi-threaded deployment. Fine for development;
not a guarantee for PyPy or sub-interpreter contexts.

**`FileSink`**
A `threading.Lock` wraps the `write() + flush()` sequence. Without
the lock, concurrent writes interleave bytes on the same line,
corrupting JSONL structure. The lock is acquired per-`emit()` call —
no batching, no async queue. Throughput is bounded by I/O speed and
lock contention; for high-throughput production use, the enterprise
Splunk or OTel sink is more appropriate.

**Enterprise sinks (Splunk HEC, Sentinel REST, OTel exporter)**
Each event is a separate HTTP POST or SDK call. HTTP clients are
connection-pool-backed and inherently concurrent-safe. Internal
batching queues (where the sink buffers events before flushing) must
use `queue.Queue` or an async queue — never a bare list.

**`RecordingSink` (test helper)**
Used in `tests/conftest.py`. Appends to `self.events: list[AuditEvent]`.
In tests that exercise concurrent code paths, `self.events` must be
a `collections.deque` with `appendleft` or guarded by a lock —
`list.append()` is GIL-safe in CPython but is not specified as
thread-safe in the language. Use a lock to be safe across runtimes.

---

## 5. Sync vs async — the one-pass decision

The current architecture is synchronous. Boundary functions are `def`,
not `async def`. Adapter methods are `def`, not `async def`.

**This is a deliberate choice for the first implementation.** Sync is
simpler to reason about, easier to test, and sufficient for most
agents. Thread-per-agent concurrency with the GIL scales to ~100–200
concurrent agents in CPython before overhead becomes material.

**If the team decides to go async**, it is a one-pass migration:

- Every `Scanner.scan`, `PolicyEngine.evaluate`, `AuditSink.emit`,
  `ToolSource.load`, `Verifier.verify` becomes `async def`.
- Every boundary function becomes `async def`.
- `Harness` facade methods become `async def`.
- All adapter implementations update simultaneously — no mixed-mode
  intermediary state.

The decision must be made before any adapter ships to customers.
Changing the Protocol from sync to async is a breaking change. Do not
ship sync `Scanner.scan()` and then try to add `async def scan()` in a
minor version.

If async is chosen, Python `asyncio` is the runtime. No `trio` or
`anyio` abstractions — one async runtime, one canonical path.

---

## 6. What does NOT require coordination

These operations are concurrent-safe without additional work:

- **`scan_input` / `scan_output`** — scanners are stateless; each call
  gets its own `ScanVerdict` instance; no shared state written.
- **`check_tool_call`** — policy is stateless; registry lookup uses
  the per-call scoped view (see §3); `GateDecision` instances are not
  shared.
- **`scope_context_for_subagent`** — pure function; returns a new
  `RuntimeContext`; writes nothing.
- **`PolicyEngine.evaluate` / `PolicyEngine.evaluate_source`** — rules
  are loaded once at startup and never mutated; evaluation is a
  read-only traversal.
- **`SecretsProvider.resolve`** — secrets are resolved at construction
  time and held as plain attributes on `ToolSource` instances; no
  runtime resolve calls during concurrent boundary calls.

---

## 7. Testing concurrency

**Unit tests** do not need concurrency. They test a single call path.

**Integration tests** (`tests/integration/`) include one concurrency
scenario:

```python
# tests/integration/test_concurrent_agents.py
def test_n_agents_same_harness(harness, make_ctx):
    """10 agents run full turns concurrently. No cross-contamination."""
    ctxs = [make_ctx(tenant_id=f"t{i}") for i in range(10)]
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(run_full_turn, harness, ctx) for ctx in ctxs]
        results = [f.result() for f in futures]
    # Every result is a (ScanVerdict, GateDecision, ScanVerdict) triple.
    # Assert no result contains a tool from a different tenant's sources.
    for i, (_, gate, _) in enumerate(results):
        if gate.allowed:
            assert gate.tool_tenant == f"t{i}"
```

**Contract tests** (`tests/contracts/sink_contract.py`) include the
concurrent-emit test described in §4.

These two test classes are the minimum safety net. Add more if
production load profiles reveal edge cases.
