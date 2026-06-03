# harness/__init__.py — the entire public API surface of the SDK.
#
# RESPONSIBILITY
#   Re-export the small, stable set of names that agent code is allowed to
#   import. Nothing else in this package is public.
#
# PUBLIC SURFACE (do not extend without a design discussion)
#   Harness          — the facade class (core.harness.Harness)
#   Tool             — tool descriptor (tools.tool.Tool)
#   ToolSource       — tool source descriptor (adapters.tool_sources.base.ToolSource)
#   AgentConfig      — agent profile model (agents.agent_config.AgentConfig)
#   RuntimeContext   — identity envelope (core.context.RuntimeContext)
#   ScanVerdict      — scan_input / scan_output return type (core.verdicts)
#   GateDecision     — check_tool_call return type (core.verdicts)
#   Finding          — individual scanner finding (core.verdicts)
#   HarnessError     — base exception (core.errors)
#
# WHAT TO IMPLEMENT
#   - Import the names above from their canonical modules and list them in
#     __all__. Re-exports only — no logic, no aliasing, no renaming.
#   - Set __version__ from package metadata (importlib.metadata).
#
# DO NOT
#   - Re-export adapter classes, boundary functions, internal types, or
#     pydantic config models. Those are internal and refactorable.
#   - Add convenience helpers, factories, or shortcut functions here.
#     The facade is Harness. There is no second way in.
