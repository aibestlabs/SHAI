# harness/adapters/tool_sources/skill.py — skill tool source.
#
# RESPONSIBILITY
#   A ToolSource that activates a named group of locally registered tools
#   on demand. Skills implement progressive disclosure — tools in a skill
#   are not surfaced to the LLM until the skill is activated for that
#   agent's turn by policy.
#
# WHAT TO IMPLEMENT
#   - SkillSource implementing ToolSource Protocol:
#       name      = "skill"
#       transport = Transport.skill
#       tags      = configurable (e.g. ["skill", "read", "internal"])
#
#       Constructor takes:
#         skill_name: str           (the name declared in harness.yaml)
#         tool_names: list[str]     (tools that belong to this skill)
#         registry:   ToolRegistry  (shared base; looked up at load time)
#
#       load(ctx) -> list[Tool]:
#           Look up each tool_name in the shared registry base.
#           Return the found tools. ToolNotRegisteredError on any miss
#           → raise ConfigError at construction time (validate tool_names
#           exist when the skill is registered, not at load time).
#           Thread-safe — registry base is read-only after startup.
#
# harness.yaml shape (for reference):
#   tool_sources:
#     - name: docs_skill
#       transport: skill
#       tools: ["search_docs", "fetch_doc", "summarise_doc"]
#       tags: ["skill", "read", "internal"]
#
# ENTRY POINT
#   Registered under harness.tool_sources as "skill".
