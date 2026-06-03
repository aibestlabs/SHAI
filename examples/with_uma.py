# examples/with_uma.py — harness + UMA composed by the agent.
#
# RESPONSIBILITY
#   Show how the agent uses BOTH packages side by side, without either
#   importing the other. This is the integration story from the
#   architectural discussion (see harness-conversation.md): the agent
#   composes; the harness governs the boundaries; UMA owns memory.
#
# WHAT TO IMPLEMENT
#   - Imports: harness AND uma. Both are public dependencies of the
#     agent code in this file. Neither package imports the other.
#   - Construct memory = UMAMemory.from_yaml("uma.yaml") and
#     harness = Harness.from_yaml("harness.yaml") side by side.
#   - The turn flow (taken from the design document):
#       async def handle_turn(user_msg, ctx):
#           if harness.scan_input(user_msg, ctx).blocked:
#               return Response.refused()
#           mem = await memory.retrieve_context(query_text=user_msg, ctx=ctx)
#           reply = await my_llm_loop(user_msg, mem, on_tool_call=
#               lambda name, args: harness.check_tool_call(name, args, ctx))
#           if harness.scan_output(reply, ctx).blocked:
#               reply = reply.redacted()
#           await memory.process_turn(user_msg=user_msg, assistant_reply=reply, ctx=ctx)
#           return reply
#   - Note in a comment that the harness's input scan can be disabled
#     in harness.yaml when relying on UMA's write-time scanning, to
#     avoid double-scanning.
#
# WHAT THIS EXAMPLE SHOWS
#   - The agent is the only thing that imports both libraries.
#   - The harness call to scan_input is the agent's choice; UMA's
#     retrieval is the agent's choice; the order is the agent's choice.
#   - check_tool_call inside the loop, scan_output before egress,
#     memory.process_turn after — exactly the data flow from the
#     architecture diagram.
#
# DO NOT
#   - Couple harness and UMA via shared types beyond RuntimeContext
#     shape. If both libraries happen to use a RuntimeContext-like
#     identity envelope, the agent constructs ONE and passes to both —
#     they do not share a class.
#   - Run UMA inside the harness or vice versa.
