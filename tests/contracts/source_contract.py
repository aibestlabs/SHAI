# tests/contracts/source_contract.py
#
# RESPONSIBILITY
#   Conformance suite every ToolSource adapter must pass.
#
# WHAT TO IMPLEMENT
#   - class ToolSourceContract:
#       source_factory: ClassVar[Callable[[], ToolSource]]
#
#       def test_name_is_stable(self): ...
#       def test_transport_is_set(self):
#           assert source.transport in Transport values
#
#       def test_load_returns_list_of_tools(self):
#           load(ctx) returns a list (possibly empty) of Tool instances.
#           Every Tool has non-empty name, valid transport, non-empty tags.
#
#       def test_load_is_thread_safe(self):
#           20 threads call load(ctx) simultaneously.
#           No exceptions. All return equivalent tool lists.
#
#       def test_load_is_credential_free(self):
#           load() must not read os.environ or call SecretsProvider.
#           Credentials are constructor-injected. Verify by monkeypatching
#           os.environ to empty and asserting load() still returns tools
#           (or an empty list for sources that legitimately return empty).
#
# DO NOT
#   - Test MCP network connectivity. Use a stub MCP server in tests.
