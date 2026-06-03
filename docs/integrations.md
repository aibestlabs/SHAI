# Framework integrations

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

One section per supported framework: LangGraph, LangChain, CrewAI,
Pydantic AI, OpenAI Agents SDK, and "hand-rolled" (Anthropic / OpenAI
SDK loops). Each section is a working recipe that copy-pastes into the
customer's codebase.

For each framework:

1. The install line (`pip install harness[<extra>]`).
2. The minimal wiring: how the integration helper is constructed and
   where it plugs in.
3. A short worked example that mirrors `examples/<framework>_agent.py`.
4. Caveats specific to that framework (lifecycle peculiarities, version
   pins, anything tricky).

Plus a final section: **No framework? No problem.** Show the
hand-rolled pattern with the three boundary calls inline. Reference
`examples/hand_rolled_loop.py`.

## What does NOT go here

- The conceptual case for boundaries. That's CLAUDE.md territory.
- A comparison of frameworks. The harness is neutral.
