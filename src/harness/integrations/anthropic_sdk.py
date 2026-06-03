# harness/integrations/anthropic_sdk.py — helper for hand-rolled loops.
#
# RESPONSIBILITY
#   Provide a small, optional helper for agent code that uses the
#   Anthropic SDK directly (no LangGraph, no LangChain). This is the
#   SMALLEST integration surface and the one to build first — it
#   validates the boundary contract without any framework noise.
#
# WHAT TO IMPLEMENT
#   - gated_dispatch(
#         tool_name: str,
#         tool_args: dict,
#         ctx: RuntimeContext,
#         *,
#         harness: Harness,
#         dispatch: Callable[[str, dict], Any],
#     ) -> Any | GateDecision
#
#       1. gate = harness.check_tool_call(tool_name, tool_args, ctx)
#       2. If not gate.allowed: return gate  (caller substitutes an
#          error tool_result from gate.deny_reason)
#       3. Otherwise: return dispatch(tool_name, gate.redacted_args or tool_args)
#
#     That's the entire function. It exists so example code reads
#     cleanly, not because the agent couldn't write the same three
#     lines inline.
#
# DO NOT
#   - Import anthropic.* unconditionally. This file should be importable
#     even when the anthropic SDK is not installed — the helper is
#     SDK-agnostic. The name reflects the typical caller, not a hard
#     dependency.
#   - Add LLM-calling logic. The agent owns the LLM call. The harness
#     does not.
#   - Cache decisions. See check_tool_call DO NOT list.
