# harness/agents/registry.py — the AgentRegistry.
#
# RESPONSIBILITY
#   Runtime-managed in-memory registry of agent definitions. Operator-driven
#   — no file watching, no automatic reload. The operator explicitly loads,
#   reloads, or deregisters agents via the facade. This is an internal
#   component; the public surface is on Harness.
#
# WHAT TO IMPLEMENT
#   - AgentRegistry class:
#       Internal state: dict[str, AgentConfig]
#
#       load(path: str | Path) -> AgentConfig:
#           1. Read and yaml.safe_load the file. IOError / YAMLError →
#              ConfigError with path context.
#           2. Validate against AgentConfig schema. ValidationError →
#              ConfigError with field path.
#           3. If agent_id not in registry: store and return.
#           4. If agent_id in registry with identical content: no-op,
#              return existing (idempotent).
#           5. If agent_id in registry with different content: raise
#              AgentConflictError. Caller must use reload() explicitly.
#
#       reload(path: str | Path) -> AgentConfig:
#           1. Validate the file (steps 1-2 of load).
#           2. If agent_id not in registry: raise AgentNotRegisteredError.
#           3. Atomically swap old definition for new. In-flight calls
#              that already read the old definition complete normally —
#              RuntimeContext carries a snapshot of allowed_tags at call
#              time; the registry swap only affects new calls.
#           Returns the new AgentConfig.
#
#       deregister(agent_id: str) -> None:
#           Remove agent from registry. Raises AgentNotRegisteredError
#           if not found. In-flight calls complete normally (they already
#           hold their RuntimeContext snapshot).
#
#       get(agent_id: str) -> AgentConfig:
#           HOT PATH. Called on every check_tool_call.
#           Raises AgentNotRegisteredError on miss.
#           Must be thread-safe for concurrent reads.
#
#       list() -> list[AgentConfig]:
#           Return all registered agents in registration order.
#           CLI / debug use only, not the hot path.
#
# CONCURRENCY
#   get() is called concurrently from multiple agent threads. The internal
#   dict must be read-safe under concurrent access. In CPython, dict reads
#   are GIL-safe. For correctness across runtimes, protect writes (load,
#   reload, deregister) with a threading.Lock while reads remain lock-free.
#
# DO NOT
#   - Watch files or trigger reloads automatically.
#   - Persist registry state to disk.
#   - Add TTLs or soft-deletes.
#   - Expose the internal dict directly.
