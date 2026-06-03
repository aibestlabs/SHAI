# tests/unit/test_tools_registry.py
#
# RESPONSIBILITY
#   Cover the InMemoryRegistry reference adapter.
#
# WHAT TO TEST
#   - register + get round-trip returns the same Tool instance.
#   - register is idempotent on identical Tool (same name, schema, tags).
#   - register raises ConfigError when a tool with the same name but
#     different schema/tags is registered second.
#   - get raises ToolNotRegisteredError on miss, with the unknown name
#     and a sample of registered names in the error message.
#   - list returns tools in insertion order.
#   - register_many is equivalent to looped register; failures inside
#     register_many surface with the offending tool's name in context.
#
# DO NOT
#   - Test thread-safety unless concurrent registration is added to
#     the implementation. Speculative tests rot.
