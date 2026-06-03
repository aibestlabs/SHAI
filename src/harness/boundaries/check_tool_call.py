# harness/boundaries/check_tool_call.py — the tool-call gate.
#
# RESPONSIBILITY
#   The mandatory boundary. For every tool the agent intends to dispatch,
#   enforce the three-layer evaluation model, emit exactly one audit event,
#   and return a GateDecision. NEVER dispatch the tool.
#
# WHAT TO IMPLEMENT
#   - One public function:
#       def run(
#           name: str,
#           args: dict[str, Any],
#           ctx: RuntimeContext,
#           *,
#           agent_registry: AgentRegistry,
#           registry_view: ScopedRegistryView,
#           policy: PolicyEngine,
#           arg_scanners: list[Scanner],
#           emitter: AuditEmitter,
#           scan_args_for_tags: set[str] = frozenset({"sensitive"}),
#       ) -> GateDecision
#
#   - Algorithm — three layers, strict order:
#
#     LAYER 1 — Agent registration + capability gate (pre-policy, fast)
#       1a. agent = agent_registry.get(ctx.agent_id).
#           AgentNotRegisteredError → deny, "agent not registered".
#       1b. Registry lookup: tool = registry_view.get(name).
#           ToolNotRegisteredError → deny, "unknown tool: <name>".
#       1c. If ctx.allowed_tags is set and tool.tags ⊄ ctx.allowed_tags:
#           deny, "tool not in agent capability set". No policy eval.
#
#     LAYER 2 — Agent-scoped policy rules
#       2. policy.evaluate(tool, args, ctx, rules=agent.policy_rules).
#          Match → use this decision. No match → continue to Layer 3.
#
#     LAYER 3 — Global policy rules
#       3. policy.evaluate(tool, args, ctx).
#          Match → use this decision. No match → default allow.
#
#     OPTIONAL ARG SCANNING
#       4. If decision is allow or redact AND tool.tags ∩ scan_args_for_tags:
#          Serialize args, run each arg_scanner. Errors logged, treated
#          as empty findings. Any finding.severity >= high → override to
#          deny, "args scan blocked: <category>".
#
#     AUDIT + RETURN
#       5. Build AuditEvent (boundary="tool_call_gate", decision=...,
#          tool_name=name, transport=tool.transport,
#          adapters=[policy.name, *scanners that ran], duration_ms).
#       6. emitter.emit(event).
#       7. Return GateDecision.
#
# INVARIANTS
#   - Exactly one AuditEvent per call. No exceptions.
#   - The harness never dispatches the tool.
#   - check_tool_call has no enabled flag — it is mandatory.
#   - When allowed=False, deny_reason is always non-empty.
#   - PolicyEvaluationError propagates after emitting a failure audit event.
#   - Layer order is fixed. No config option changes it.
#   - No special routing based on transport type. All tools go through
#     the same three-layer evaluation. Stricter rules for specific tool
#     types (e.g. code_execution) are expressed in policy, not here.
#
# DO NOT
#   - Cache decisions across calls.
#   - Mutate args in place.
#   - Add transport-specific branching. Tags + policy rules handle that.
