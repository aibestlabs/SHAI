# harness/core/context.py — RuntimeContext, the identity envelope.
#
# RESPONSIBILITY
#   Define the identity scope every boundary call carries: who is calling,
#   on behalf of whom, in what tenant, in what session. This is the
#   envelope — it is NOT memory context, NOT prompt context, NOT user
#   message content. Just identity.
#
# WHAT TO IMPLEMENT
#   - RuntimeContext as a frozen pydantic model (or frozen dataclass +
#     pydantic validator if a dataclass is enough). Fields:
#       tenant_id: str       (required, non-empty)
#       agent_id:  str       (required, non-empty)
#       user_id:   str | None
#       session_id: str | None
#       request_id: str | None   (optional, useful for tracing)
#     All other context — memory, prompt, retrieval — belongs to the
#     agent, not here. Resist adding fields.
#   - A `to_log_fields()` method that returns the canonical logging dict
#     using the exact field names listed in CLAUDE.md §6 (`tenant_id`,
#     `agent_id`, `user_id`, `session_id`). Every logger in the codebase
#     uses this — never hand-build the dict elsewhere.
#
# DO NOT
#   - Add memory, prompt, retrieved-document, or LLM-related fields.
#   - Make RuntimeContext mutable. Boundaries should not mutate scope.
#   - Add a `from_request()` factory specific to any web framework —
#     construction is the agent's job.
