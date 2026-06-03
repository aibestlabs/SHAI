# tests/unit/test_config_loader.py
#
# RESPONSIBILITY
#   Cover config/loader.py and config/resolution.py.
#
# WHAT TO TEST
#   - load_yaml returns a HarnessConfig for the canonical fixture.
#   - load_yaml raises ConfigError on missing file, malformed YAML,
#     and extra unknown fields (extra="forbid" on the schema).
#   - ${ENV_VAR} interpolation:
#       - Present env var → substituted.
#       - Missing env var → ConfigError naming the variable.
#       - Substring inside larger string → substituted in place.
#   - secret://name interpolation:
#       - Exact-match string → resolved via SecretsProvider.
#       - Substring secret reference → ConfigError (must be exact-match
#         per resolution.py).
#       - Missing secret → ConfigError.
#   - Boundary validators fire:
#       - scanners=[] with enabled=True → ConfigError.
#       - audit_sinks=[] → ConfigError.
#
# DO NOT
#   - Mock os.environ at module load. Use monkeypatch fixtures per test.
