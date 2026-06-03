# examples/langgraph_agent.py — LangGraph + harness example.
#
# RESPONSIBILITY
#   Demonstrate harness.integrations.langgraph.HarnessGate wired into a
#   minimal LangGraph graph. Shows the difference between scan_input /
#   scan_output (called by the agent code at turn boundaries) and the
#   tool gate (wired as a graph node).
#
# WHAT TO IMPLEMENT
#   1. Build a tiny StateGraph with three nodes: agent → harness_gate →
#      tool_executor. The harness_gate node is HarnessGate(harness,
#      ctx_provider=lambda state: state["ctx"]).
#   2. Outside the graph, wrap the per-turn entry point with
#      scan_input before graph.invoke and scan_output after.
#   3. Register two example tools the agent might call (read-only and
#      external_write) so the example exercises both allow and deny
#      paths.
#   4. main() runs three sample turns and prints emitted audit events.
#
# DO NOT
#   - Push scan_input / scan_output INTO the graph as nodes. They are
#     per-turn boundaries; pushing them in as nodes muddies the
#     separation between turn lifecycle (agent's job) and tool gating
#     (graph's job).
