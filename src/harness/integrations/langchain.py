# harness/integrations/langchain.py — LangChain tool wrapping.
#
# RESPONSIBILITY
#   Provide a `wrap_tool` helper that returns a LangChain-compatible
#   tool whose execution path is gated by harness.check_tool_call.
#   Optional — loaded only when `harness[langchain]` is installed.
#
# WHAT TO IMPLEMENT
#   - wrap_tool(tool: BaseTool, *, harness: Harness, ctx_provider: Callable[[], RuntimeContext]) -> BaseTool
#       Returns a new BaseTool (or BaseTool subclass instance) whose
#       _run / _arun method:
#         1. ctx = ctx_provider()
#         2. gate = harness.check_tool_call(tool.name, args, ctx)
#         3. If denied: return gate.deny_reason as the tool output
#            (LangChain treats the string as the tool's reply).
#         4. If allowed: delegate to the original tool with
#            (gate.redacted_args or args).
#
#   - Optional CallbackHandler that hooks on_tool_start to call
#     check_tool_call. The wrap_tool path is preferred (the gate runs
#     even if the user forgets to wire the handler); the callback path
#     is a fallback for codebases where tool wrapping is awkward.
#
# DO NOT
#   - Subclass BaseTool with a new public class. The wrapper is a
#     transient object; the customer keeps thinking in terms of their
#     own tools.
#   - Import langchain_core unconditionally — deferred import like
#     langgraph.py.
