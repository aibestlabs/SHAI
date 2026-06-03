# Tool sources, MCP gateway, and skills

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

The complete reference for ToolSource — the unified concept covering
local tools, MCP servers, and skills.

Sections:

1. **Concept** — what a ToolSource is, why it exists, how it differs from
   a Tool. A Tool is a callable descriptor; a ToolSource is where tools
   come from. The distinction exists so policy can decide which sources
   are active for a given agent turn.

2. **Three transport kinds** — local, mcp, skill, sandbox. What each means,
   when to use each, what credentials (if any) are required.

3. **harness.yaml tool_sources section** — field-by-field reference for
   declaring sources. Show a complete example for each transport kind.

4. **Credential resolution** — how MCP source credentials use secret://
   references, when they are resolved (at Harness.from_yaml(), not at
   load time), and why load() is credential-free.

5. **Source activation** — how PolicyEngine.evaluate_source() decides which
   sources are active per turn per agent. The agent's sources list in
   agent-xx.yaml restricts which declared sources are candidates. Policy
   can further suppress sources. Show the activation flow.

6. **ScopedRegistryView** — why source-loaded tools go into a per-agent
   per-turn view rather than the shared registry. How the view is created,
   passed through load_sources → check_tool_call, and discarded.

7. **Skills** — how skill sources implement progressive disclosure. Tools
   in a skill are not visible to the LLM until the skill is activated.
   Show a worked example.

8. **SourceRegistry** — the internal component that orchestrates activation.
   Its relationship to load_sources on the facade.

## What does NOT go here

- Policy rule grammar (lives in docs/policy.md).
- How to write a new adapter (lives in docs/adapters.md).
- Audit event details (lives in docs/audit-schema.md).
