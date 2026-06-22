# Audit Event Schema

Every boundary call emits exactly one `AuditEvent`. No field ever contains raw user input, LLM output, tool arguments, or scanner-matched substrings.

---

## AuditEvent fields

| Field | Type | Always present | Description |
|---|---|---|---|
| `timestamp` | `datetime` (UTC, ISO 8601) | ✓ | When the boundary was called |
| `boundary` | `input_scan \| tool_call_gate \| output_scan` | ✓ | Which boundary emitted this event |
| `decision` | `allow \| deny \| redact \| blocked` | ✓ | Outcome |
| `disabled` | `bool` | ✓ | True if boundary was disabled in config |
| `duration_ms` | `int` | ✓ | Wall-clock time from boundary entry to emit |
| `tenant_id` | `str` | ✓ | From `harness.yaml → tenant_id`. Default `"default"` |
| `agent_id` | `str` | ✓ | From `RuntimeContext.agent_id` |
| `sub_agent_id` | `str \| null` | — | Set for subagent turns |
| `tool_name` | `str \| null` | gate only | Tool that was gated |
| `transport` | `str \| null` | gate only | `local \| mcp \| skill` |
| `adapters` | `list[str]` | — | Names of scanners or policy engine that ran |
| `finding_count` | `int` | — | Number of findings (scan boundaries only) |
| `max_severity` | `info \| low \| medium \| high \| critical \| null` | — | Highest finding severity |
| `deny_reason` | `str \| null` | when denied | Operator-authored rule text or harness internal reason |
| `audit_tags` | `dict[str, str]` | — | From `AgentConfig.audit_tags` |
| `extra` | `dict[str, Any]` | — | Caller-supplied metadata (never auto-populated) |

---

## Cross-field constraints (enforced at construction)

- `decision=deny` requires `deny_reason` to be non-null.
- `decision=blocked` is only valid on `input_scan` and `output_scan`.
- `decision=deny` is only valid on `tool_call_gate`.
- `disabled=True` requires `decision=allow` and `finding_count=0`.

---

## Decision values by boundary

| Boundary | Possible decisions |
|---|---|
| `input_scan` | `allow`, `blocked`, `allow` (disabled) |
| `tool_call_gate` | `allow`, `deny`, `redact` |
| `output_scan` | `allow`, `blocked`, `allow` (disabled) |

---

## JSONL output (StdoutSink)

Each event is one line of JSON. `null` fields are omitted.

```json
{
  "timestamp": "2025-01-15T10:23:45.123456+00:00",
  "boundary": "tool_call_gate",
  "decision": "deny",
  "disabled": false,
  "duration_ms": 2,
  "tenant_id": "platform-prod",
  "agent_id": "orchestrator_agent",
  "sub_agent_id": "research_sub",
  "tool_name": "send_email",
  "transport": "local",
  "adapters": ["rules"],
  "deny_reason": "external_write requires explicit permission",
  "audit_tags": {"team": "platform", "env": "prod"}
}
```

---

## SIEM query examples

**All denied tool calls in the last hour:**
```
boundary="tool_call_gate" AND decision="deny"
```

**PII detections above medium severity:**
```
boundary="input_scan" AND max_severity IN ["high", "critical"]
```

**All events for a specific agent across all tenants:**
```
agent_id="orchestrator_agent"
```

**Subagent turning privilege isolation violations:**
```
sub_agent_id=* AND decision="deny" AND deny_reason="*capability set*"
```

---

## What is never in an AuditEvent

- The user's message text
- The LLM's response text
- Tool arguments or return values
- The matched substring from a scanner finding
- Credentials or secret values
- Any PII beyond what operators explicitly put in `audit_tags`

`Finding.detail` contains only category names and short notes — never the matched text.

---

## tenant_id in multi-deployment setups

Each `Harness` instance reads `tenant_id` from `harness.yaml`. When running multiple harness instances (multiple processes), give each a distinct `tenant_id` so log partitioning works:

```yaml
# deployment-a/config/harness.yaml
tenant_id: "platform-prod-eu"

# deployment-b/config/harness.yaml
tenant_id: "platform-prod-us"
```
