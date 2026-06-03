# tests/contracts/__init__.py
#
# CRITICAL: This package defines the Protocol-conformance suites that
# EVERY adapter implementation — in harness, in harness-enterprise, in
# third-party packages — must pass. The suites are published as
# reusable pytest classes / fixtures.
#
# This is the open-core enforcement mechanism. See CLAUDE.md §6 "Test
# the contract, not the implementation."
#
# DO NOT
#   - Put implementation-specific tests here. Those live in
#     tests/unit/test_<adapter>.py.
#   - Import from harness_enterprise. The contract suite must run with
#     core alone; harness-enterprise IMPORTS this suite, not the
#     other way around.
