# harness/core/types.py — shared enums and type aliases used across modules.
#
# RESPONSIBILITY
#   Hold the small, stable enums and aliases referenced by verdicts, events,
#   and config. Nothing here depends on any other harness module — this file
#   sits at the bottom of the import graph.
#
# WHAT TO IMPLEMENT
#   - BoundaryName: StrEnum with values:
#       "input_scan"      — scan_input boundary
#       "tool_call_gate"  — check_tool_call boundary
#       "output_scan"     — scan_output boundary
#
#   - Decision: StrEnum with values:
#       "allow"   — tool call permitted or scan passed
#       "deny"    — tool call blocked by policy or agent not registered
#       "redact"  — tool call permitted with redacted args
#       "blocked" — scan boundary blocked the content
#
#   - Severity: StrEnum with values:
#       "info", "low", "medium", "high", "critical"
#
#   - Transport: StrEnum with values:
#       "local"  — Python function registered at startup
#       "mcp"    — remote MCP server
#       "skill"  — named group of local tools activated on demand
#
# DO NOT
#   - Import anything from harness.* (except stdlib).
#   - Add behavior. Enums and aliases only.
#   - Invent variant casings. Logging fields must match these exactly
#     (see CLAUDE.md §6).
#   - Add a "sandbox" transport — sandbox enforcement is a policy concern,
#     expressed via tool tags and policy rules, not a transport type.
