# harness/integrations/openai_agents.py — OpenAI Agents SDK lifecycle hook.
#
# RESPONSIBILITY
#   Provide a `harness_hook` factory that returns a before_tool_call
#   lifecycle hook for the OpenAI Agents SDK. Optional — loaded only
#   when `harness[openai-agents]` is installed.
#
# WHAT TO IMPLEMENT
#   - harness_hook(harness: Harness, ctx_provider) -> Hook
#       Returns an object the SDK accepts in its hooks=... parameter.
#       On before_tool_call(tool_name, args):
#         1. ctx = ctx_provider()
#         2. gate = harness.check_tool_call(tool_name, args, ctx)
#         3. On deny, raise the SDK's "cancel tool" exception with
#            gate.deny_reason as the reason.
#         4. On allow, return gate.redacted_args or args (the SDK uses
#            the returned dict as the effective args).
#
#   - The shape of the lifecycle hook depends on the SDK version we
#     target. Document the version in the module docstring.
#
# DO NOT
#   - Hook into other lifecycle events (before_llm_call, after_run).
#     The harness gates tools, not turns; scan_input/scan_output remain
#     the agent's responsibility to call.
