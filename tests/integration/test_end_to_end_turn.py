# tests/integration/test_end_to_end_turn.py
#
# RESPONSIBILITY
#   Exercise a full turn through a real Harness built from
#   tests/fixtures/harness.yaml. No mocks beyond the recording audit
#   sink.
#
# WHAT TO TEST
#   - Happy path: clean user message → scan_input allow, check_tool_call
#     allow for a known tool, scan_output allow. Exactly THREE
#     AuditEvents emitted in order: input_scan, tool_call_gate,
#     output_scan.
#   - Input PII blocking: a user message containing an SSN-like pattern
#     → scan_input blocks. AuditEvent decision="blocked".
#   - Tool deny by policy: a tool tagged "external_write" → gate denies
#     under the test policy's deny rule for tenant t1. AuditEvent
#     decision="deny".
#   - Output egress catch: a synthetic LLM output containing a credit
#     card number → scan_output blocks, redacted_text populated.
#
#   - Audit events stream through the FileSink correctly when the
#     fixture is loaded with audit_sinks=[file] (use tmp_path).
#
# DO NOT
#   - Mock any reference adapter in these tests. The point is to verify
#     they compose correctly.
#   - Hit the network. No production adapters in integration tests for
#     core; harness-enterprise has its own integration suite.
