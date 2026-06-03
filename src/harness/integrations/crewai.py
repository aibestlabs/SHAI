# harness/integrations/crewai.py — CrewAI tool gating.
#
# RESPONSIBILITY
#   Provide a `wrap_tool` helper for CrewAI's Tool class. Optional —
#   loaded only when `harness[crewai]` is installed.
#
# WHAT TO IMPLEMENT
#   - wrap_tool(tool, *, harness: Harness, ctx_provider) -> Tool
#       Same pattern as integrations/langchain.py:
#         1. Resolve ctx.
#         2. Call harness.check_tool_call.
#         3. On deny, return gate.deny_reason.
#         4. On allow, delegate to the original tool with potentially
#            redacted args.
#
#   - CrewAI tool execution flows through Tool._run / Tool.run; subclass
#     just enough to intercept that path.
#
# DO NOT
#   - Hook into CrewAI's agent loop. Boundary integration is at the
#     tool level only.
#   - Add a CrewAI-specific Tool descriptor that diverges from the
#     harness Tool type. One Tool class, one canonical path.
