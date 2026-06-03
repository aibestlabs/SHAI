# harness/integrations/langgraph.py — LangGraph gate node wrapper.
#
# RESPONSIBILITY
#   Wire the harness's tool gate into a LangGraph graph as a node that
#   sits in front of the tool-executor node. Optional — only loaded by
#   customers who install `harness[langgraph]`.
#
# WHAT TO IMPLEMENT
#   - HarnessGate class or factory:
#       Constructor: (harness: Harness, ctx_provider: Callable[[dict], RuntimeContext])
#         - ctx_provider extracts the RuntimeContext from the LangGraph
#           state dict. The harness does not assume where the context
#           lives in state — the customer wires it.
#
#       __call__ / invoke(state) -> state:
#         - Read the pending tool call from state (LangGraph's
#           tool-call attribute on the last AIMessage).
#         - For each pending tool call:
#             gate = self.harness.check_tool_call(name, args, ctx_provider(state))
#             If denied: replace the tool call with a synthetic
#               ToolMessage(content=gate.deny_reason) so the LLM sees
#               the refusal in the next turn.
#             If allowed with redacted_args: replace the args before
#               passing through.
#             If allowed: pass through unchanged.
#         - Return updated state. The tool executor node downstream
#           runs the (possibly modified) tool calls.
#
#   - The framework SDK import (`langgraph`) happens inside the class
#     body or via a deferred import; the module imports cleanly without
#     langgraph installed.
#
# DO NOT
#   - Re-implement scan_input / scan_output as LangGraph nodes. Those
#     are turn-level boundaries, not tool-level; the agent's main graph
#     calls them at the start/end of a turn, not as nodes between tools.
#   - Bypass check_tool_call by inspecting the tool registry directly.
#     Always go through the facade.
