# tests/unit/test_adapters_discovery.py
#
# RESPONSIBILITY
#   Cover adapters/discovery.py.
#
# WHAT TO TEST
#   - resolve returns the right class for each reference adapter name
#     (regex_pii, basic_injection, rules, stdout, file, memory, env).
#   - resolve on unknown name raises AdapterDiscoveryError with the
#     unknown name AND list_registered output included in the message.
#   - list_registered returns every registered name for each canonical
#     group.
#   - When two entry points claim the same (group, name): the second
#     access raises AdapterDiscoveryError with both class paths in the
#     message (we install a temporary entry point in the test to set
#     this up).
#
# DO NOT
#   - Test that production adapters (purview, opa) resolve. They live
#     in harness-enterprise; cross-package resolution is exercised
#     there.
