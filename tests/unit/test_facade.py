# tests/unit/test_facade.py
#
# RESPONSIBILITY
#   Cover the Harness facade (core/harness.py): from_yaml construction,
#   register_tools idempotency, and delegation to boundary functions.
#
# WHAT TO TEST
#   - Harness.from_yaml on the canonical fixture loads cleanly and
#     instantiates every adapter named in the config.
#   - from_yaml on a malformed YAML raises ConfigError with the file
#     path in the message.
#   - from_yaml on a config referencing an unknown adapter name raises
#     AdapterDiscoveryError naming the unresolved name and listing the
#     installed candidates.
#   - register_tools accepts an iterable; idempotent on duplicate Tool
#     with identical shape; raises ConfigError on conflicting shape for
#     the same name.
#   - Each boundary method on Harness calls into the corresponding
#     boundaries.* function with the right adapter dependencies. A
#     light spy on the boundary function is enough; we don't need to
#     re-test boundary behavior here.
#
# DO NOT
#   - Add tests that exercise boundary logic. Boundary tests own that.
#     The facade tests only verify wiring.
