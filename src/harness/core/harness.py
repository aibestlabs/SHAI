# harness/core/harness.py — the Harness facade.
#
# RESPONSIBILITY
#   The ONLY public entry point of the SDK. Holds configured adapter
#   instances and the AgentRegistry. Delegates every operation to the
#   appropriate internal module. No business logic lives here.
#
# WHAT TO IMPLEMENT
#   - Harness class. Constructor takes HarnessConfig plus instantiated
#     adapters and AgentRegistry. Direct construction is internal —
#     customers use from_yaml.
#
#   - Harness.from_yaml(path) -> Harness:
#       1. config.loader.load_yaml(path) → HarnessConfig
#       2. Resolve adapters via adapters.discovery.resolve(group, name)
#       3. Instantiate adapters, passing resolved secrets where needed
#       4. Construct AuditEmitter with resolved sinks
#       5. Construct AgentRegistry
#       6. Return Harness
#       Failures raise ConfigError, AdapterDiscoveryError, AdapterInitError.
#
#   AGENT MANAGEMENT (operator-driven, explicit):
#
#   - load_agent(path) -> AgentConfig:
#       Validate and register an agent-xx.yaml. Raises AgentConflictError
#       if agent_id already registered with different content.
#
#   - reload_agent(path) -> AgentConfig:
#       Validate and atomically replace an existing agent definition.
#       Keeps old definition and raises ConfigError if file is invalid.
#       Raises AgentNotRegisteredError if agent_id unknown.
#
#   - deregister_agent(agent_id) -> None:
#       Remove agent. In-flight calls complete against the old definition.
#
#   - list_agents() -> list[AgentConfig]:
#       Return all registered agents. CLI / debug use only.
#
#   STARTUP:
#
#   - register_tools(tools) -> None:
#       Delegate to ToolRegistry. Idempotent on identical Tool.
#       Raises ConfigError on conflicting schema for same name.
#
#   PER-TURN:
#
#   - load_sources(ctx) -> list[Tool]:
#       Obtain ScopedRegistryView, activate sources via policy, load
#       tools into view, return active tool list. Credential-free.
#       Never writes to shared ToolRegistry base.
#
#   - scan_input(text, ctx) -> ScanVerdict:
#       Delegate to boundaries.scan_input.run(...)
#
#   - check_tool_call(name, args, ctx, *, registry_view=None) -> GateDecision:
#       Delegate to boundaries.check_tool_call.run(...)
#       registry_view is the ScopedRegistryView from load_sources.
#
#   - scan_output(text, ctx) -> ScanVerdict:
#       Delegate to boundaries.scan_output.run(...)
#
#   SUBAGENT:
#
#   - scope_context_for_subagent(parent_ctx, allowed_tags) -> RuntimeContext:
#       Pure function. Asserts child.allowed_tags ⊆ parent.allowed_tags.
#       Sets parent_agent_id on the child context. No adapter calls.
#
# DO NOT
#   - Put boundary logic, policy evaluation, or source activation here.
#   - Expose adapter instances on the public surface.
#   - Add a close() / context-manager unless adapters genuinely need cleanup.
#   - Store per-turn state (ScopedRegistryView) on the instance.
