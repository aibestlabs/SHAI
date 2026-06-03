# harness/tools/tool.py — the Tool descriptor.
#
# RESPONSIBILITY
#   Describe ONE tool the agent might dispatch. Metadata only —
#   never an executable callable. The harness gates; the agent dispatches.
#   Tool is PART OF THE PUBLIC API.
#
# WHAT TO IMPLEMENT
#   - Tool as a frozen pydantic model:
#       name:        str
#           Unique within a registry. Non-empty.
#       schema:      Any
#           The args schema — pydantic model class, JSON schema dict, or
#           whatever the registered toolkit uses. The harness stores and
#           surfaces it to PolicyEngine; it does not interpret it.
#       tags:        list[str]
#           Classification labels: "read", "external_write", "sensitive",
#           "internal", "code_execution", etc. These are what declarative
#           policy rules match on. Tags are the mechanism for marking
#           tools that need stricter policy — including code-execution
#           tools that would previously have been called "sandbox".
#       transport:   Transport
#           One of: local | mcp | skill
#       description: str | None
#           Free-form. Not included in audit events by default.
#
#   - Equality: two Tool instances are equal iff name + schema + tags +
#     transport match. Used by the registry to detect conflicts.
#
# DO NOT
#   - Make Tool callable.
#   - Validate or interpret schema.
#   - Add a "sandbox" transport value — removed. Use tags instead
#     (e.g. tags=["code_execution"]) and write policy rules on those tags.
