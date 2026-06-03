# harness/integrations/pydantic_ai.py — Pydantic AI tool gating.
#
# RESPONSIBILITY
#   Provide a `wrap_tool` helper compatible with Pydantic AI's @agent.tool
#   decorator and its validator hook. Optional — loaded only when
#   `harness[pydantic-ai]` is installed.
#
# WHAT TO IMPLEMENT
#   - wrap_tool(fn, *, harness: Harness, tool_name: str, ctx_provider)
#       Returns a callable suitable for registration with Pydantic AI.
#       Internally:
#         1. Resolve ctx.
#         2. Call harness.check_tool_call(tool_name, kwargs, ctx).
#         3. On deny, raise / return a ModelRetry-style sentinel that
#            surfaces the deny_reason to the model.
#         4. On allow, call fn(**(redacted_args or kwargs)).
#
#   - Optional alternative: a system-message validator that intercepts
#     tool-call structured outputs before dispatch. Use whichever path
#     is more idiomatic in the Pydantic AI version we target — document
#     the version in the module docstring once chosen.
#
# DO NOT
#   - Reinvent Pydantic AI's tool argument validation. The framework
#     does that; the harness only gates.
#   - Couple the wrapper to a specific Pydantic AI version's internal
#     API. Use the public agent.tool / agent.tool_plain surface.
