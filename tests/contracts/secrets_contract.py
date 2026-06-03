# tests/contracts/secrets_contract.py
#
# RESPONSIBILITY
#   Conformance suite every SecretsProvider adapter must pass.
#
# WHAT TO IMPLEMENT
#   - class SecretsProviderContract:
#       provider_factory: ClassVar[Callable[[], SecretsProvider]]
#       The factory must pre-populate the provider with a known secret
#       under the name "test_secret" with value "shh".
#
#       def test_resolve_returns_value_for_known_ref(self):
#         provider.resolve("secret://test_secret") == "shh"
#
#       def test_resolve_missing_raises_config_error(self):
#         resolve("secret://does_not_exist") → ConfigError.
#
#       def test_resolve_invalid_ref_raises_config_error(self):
#         resolve("not-a-secret-ref") → ConfigError.
#
#       def test_resolve_never_returns_empty_string(self):
#         Empty values must surface as ConfigError, not as "".
#
# DO NOT
#   - Log the test secret value in test output, even on assertion
#     failure. Use opaque assertions.
