# examples/hand_rolled_loop.py — the canonical reference agent.
#
# THIS FILE IS THE LOAD-BEARING EXAMPLE.
# Every design decision in CLAUDE.md should be visible here. Read this
# before designing anything new (see CLAUDE.md §7).
#
# WHAT TO IMPLEMENT
#   A complete, runnable, no-framework agent showing the three
#   boundaries wired correctly. The structure to follow:
#
#   1. Imports — only harness types and stdlib. (LLM client is
#      simulated with a tiny stub function so the example runs without
#      an API key.)
#   2. Harness construction — Harness.from_yaml("./harness.yaml").
#   3. Tool registration — two tools: one "search_docs" (tags=["read",
#      "internal"]) and one "send_email" (tags=["external_write",
#      "sensitive"]).
#   4. The turn function — `def handle_turn(user_msg, ctx) -> str`:
#        - harness.scan_input → if blocked, return refusal
#        - run the LLM loop (stubbed, but accepts tool calls):
#            for each tool call the LLM emits:
#                gate = harness.check_tool_call(name, args, ctx)
#                if not gate.allowed:
#                    feed gate.deny_reason back as tool result
#                else:
#                    dispatch the tool (real Python function call)
#                    with gate.redacted_args or args
#                    feed result back to the LLM
#        - harness.scan_output → if blocked, redact the response
#        - return the final text
#   5. main() — three sample turns demonstrating allow, deny, and
#      block paths. Print the events from a recording sink (or just
#      tail the stdout sink that the YAML configures).
#
# WHAT THIS EXAMPLE SHOWS
#   - The agent owns the loop.
#   - The harness does not import an LLM SDK.
#   - Memory (UMA) is intentionally absent — that's a separate example
#     (examples/with_uma.py).
#   - The three boundary calls are explicit one-liners. No magic.
#
# DO NOT
#   - Wrap the loop in a helper class. The reader should see the
#     three calls inline.
#   - Use any framework integration. The whole point is "no framework
#     needed."
#   - Persist anything. This is illustration, not a production app.
