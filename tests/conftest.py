# tests/conftest.py — shared pytest fixtures.
#
# RESPONSIBILITY
#   Provide the small set of fixtures every test file relies on:
#     - A canonical RuntimeContext.
#     - A built Harness from the canonical fixtures/harness.yaml.
#     - A recording AuditSink that captures emitted events for
#       assertions.
#     - A spy ToolRegistry preloaded with a couple of tools.
#
# WHAT TO IMPLEMENT
#   - @pytest.fixture ctx() -> RuntimeContext
#       Returns a stable test context (tenant_id="t1", agent_id="a1",
#       user_id="u1", session_id="s1").
#
#   - @pytest.fixture recording_sink() -> RecordingSink
#       RecordingSink is a small AuditSink that appends events to a list.
#       Tests assert on .events after calling boundary methods. Defined
#       inline here — it's a test helper, not a public adapter.
#
#   - @pytest.fixture harness(tmp_path, recording_sink) -> Harness
#       Loads tests/fixtures/harness.yaml, overriding the audit_sinks
#       wiring to use the recording_sink. Returns a fully built Harness
#       ready for boundary calls.
#
#   - Any helper that constructs a sample Tool, sample args, etc.
#     Keep these tiny; tests should read top-to-bottom without indirection.
#
# DO NOT
#   - Mock individual adapters across the suite. Tests use REAL reference
#     adapters where possible — that's what they're for. Mocks are
#     reserved for tests of code that talks to the network or filesystem
#     in ways the reference adapters don't.
#   - Define fixtures here that are only used in one test file. Move
#     those to the test file or a sibling conftest.py.
