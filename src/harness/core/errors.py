# harness/core/errors.py — exception hierarchy.
#
# RESPONSIBILITY
#   Define HarnessError and its subclasses. Every exception raised by
#   harness code derives from HarnessError so callers can catch the
#   whole library with one except clause.
#
# WHAT TO IMPLEMENT
#   - HarnessError(Exception): base class. Constructor accepts a message
#     plus optional structured fields (tenant_id, agent_id, adapter,
#     boundary, op). Structured fields are EXPOSED as attributes for log
#     formatters — not just in the message string. See CLAUDE.md §6.
#
#   - Subclasses:
#       ConfigError(HarnessError)
#           Invalid harness.yaml or agent-xx.yaml content.
#
#       AdapterDiscoveryError(HarnessError)
#           Adapter name in config cannot be resolved to a registered
#           entry point.
#
#       AdapterInitError(HarnessError)
#           Adapter constructor failed (bad credentials, unreachable
#           backend, etc.).
#
#       AgentNotRegisteredError(HarnessError)
#           agent_id not found in AgentRegistry. check_tool_call maps
#           this to a deny decision — it does not propagate to the agent.
#
#       AgentConflictError(HarnessError)
#           load_agent called for an agent_id already registered with
#           different content. Caller must use reload_agent explicitly.
#
#       ToolNotRegisteredError(HarnessError)
#           Registry lookup miss in check_tool_call. Maps to deny.
#
#       PolicyEvaluationError(HarnessError)
#           Policy engine failed to evaluate (bad bundle, network failure).
#           A normal deny is a PolicyDecision, not an exception.
#
#       AuditEmissionError(HarnessError)
#           ALL configured sinks failed. Single sink failure is logged
#           and swallowed; total failure surfaces here.
#
# DO NOT
#   - Add subclasses for cases boundaries already handle via decisions.
#     ScanBlockedError does not exist — blocking is a ScanVerdict, not
#     an exception.
#   - Allow exceptions without context fields when those fields are
#     available.
