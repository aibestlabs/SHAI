# harness/integrations/__init__.py
#
# Framework wiring helpers. Each module is a thin wrapper around
# Harness.check_tool_call — the only harness boundary that frameworks
# need to intercept. scan_input and scan_output are turn-level and
# remain the agent's responsibility to call.
#
# Six integrations ship in core:
#
#   anthropic_sdk.py   — gated_dispatch for hand-rolled SDK loops
#                        (canonical reference; read this first)
#   langgraph.py       — HarnessGate node (agent → gate → tool_executor)
#   langchain.py       — wrap_tool() returning a gated BaseTool
#   crewai.py          — wrap_tool() intercepting Tool._run
#   pydantic_ai.py     — wrap_tool() for @agent.tool pattern
#   openai_agents.py   — harness_hook() for before_tool_call lifecycle
#
# CONVENTION FOR ALL INTEGRATIONS
#   - Framework SDK import is lazy (inside the wrapper function or class),
#     never at module top-level. The module must be importable without
#     the framework installed.
#   - No new public types. Wire types are Tool, RuntimeContext, GateDecision.
#   - No logic beyond: get ctx → call check_tool_call → on deny surface
#     deny_reason → on allow dispatch with redacted_args or original args.
#   - Framework extras are declared in pyproject.toml optional-dependencies.
