# harness/adapters/tool_sources/local.py — local tool source.
#
# RESPONSIBILITY
#   A ToolSource that surfaces tools already registered in the shared
#   ToolRegistry base via register_tools(). This is the simplest source —
#   no network, no credentials, no dynamic loading. Its purpose is to
#   make statically registered tools visible through the source activation
#   model so policy can decide whether to include them for a given agent.
#
# WHAT TO IMPLEMENT
#   - LocalSource implementing ToolSource Protocol:
#       name      = "local"
#       transport = Transport.local
#       tags      = configurable (e.g. ["internal", "read"])
#
#       Constructor takes a reference to the shared ToolRegistry base
#       and an optional tag filter (only surface tools matching these tags).
#
#       load(ctx) -> list[Tool]:
#           Return tools from the shared base whose tags match the
#           agent's allowed_tags in ctx. No network call. Thread-safe
#           (registry base is read-only after startup).
#
# ENTRY POINT
#   Registered under harness.tool_sources as "local".
