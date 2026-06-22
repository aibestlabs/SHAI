# Writing Adapters

SHAI discovers adapters via Python entry points. Any package can contribute adapters by registering them under the appropriate group. The harness resolves them by name at startup.

---

## Entry point groups

| Group | Interface | Reference impl |
|---|---|---|
| `harness.scanners` | `Scanner` Protocol | `regex_pii`, `basic_injection` |
| `harness.policy` | `PolicyEngine` Protocol | `rules` |
| `harness.audit_sinks` | `AuditSink` Protocol | `stdout`, `file` |
| `harness.tool_registry` | `ToolRegistry` Protocol | `memory` |
| `harness.tool_sources` | `ToolSource` Protocol | `local`, `skill` |
| `harness.secrets` | `SecretsProvider` (resolve method) | `env` |

---

## Scanner

```python
from harness.adapters.scanners.base import ScanResult, Scanner
from harness.core.context import RuntimeContext
from harness.core.verdicts import Finding
from harness.core.types import Severity

class MyScanner:
    name = "my_scanner"   # matches entry point name

    async def scan(self, text: str, ctx: RuntimeContext) -> ScanResult:
        findings = []
        # Inspect text
        # NEVER put matched substrings in Finding.detail
        if "bad_pattern" in text:
            findings.append(Finding(
                scanner=self.name,
                category="my.category",
                severity=Severity.HIGH,
                detail="my.category pattern detected",
            ))
        return ScanResult(
            findings=findings,
            redacted_text=text.replace("bad_pattern", "[REDACTED]") if findings else None,
        )
```

**Rules:**
- `async def scan(...)` — always async even if it returns immediately
- `Finding.detail` — category + note only, never the matched substring
- `redacted_text` — return `None` if nothing was redacted (not an empty string)
- Raise freely on hard errors; the boundary catches and logs per-scanner exceptions

---

## AuditSink

```python
from harness.core.events import AuditEvent

class MySink:
    name = "my_sink"

    async def emit(self, event: AuditEvent) -> None:
        # Ship the event. Raise on failure — AuditEmitter handles it.
        ...

    async def close(self) -> None:
        # Flush and release resources
        ...
```

**Rules:**
- `emit()` must be safe for concurrent async calls
- `close()` must be idempotent
- Raise on failure — never swallow exceptions silently (the emitter handles partial failures)
- Never log `event.extra` raw values — they may contain operator metadata

---

## PolicyEngine

```python
from harness.policy.engine import PolicyDecision, SourceDecision

class MyPolicy:
    name = "my_policy"

    async def evaluate(self, tool, args, ctx, *, rules=None) -> PolicyDecision:
        # rules = agent-scoped rules, evaluated before your global rules
        # Return PolicyDecision(action="allow") on default allow
        ...

    async def evaluate_source(self, source, ctx) -> SourceDecision:
        return SourceDecision(active=True)   # default
```

**Rules:**
- Raise `PolicyEvaluationError` on engine failure (bad bundle, network error)
- A normal deny is a `PolicyDecision(action="deny", reason=...)`, not an exception
- `evaluate_source` defaults to active — suppress only when a rule explicitly suppresses

---

## SecretsProvider

```python
class MySecrets:
    name = "my_secrets"

    def resolve(self, ref: str) -> str:
        # ref is "secret://VAR_NAME"
        # Return the plaintext value. Never log it.
        # Raise ConfigError on miss.
        ...
```

**Rules:**
- `resolve()` is synchronous — called once at startup
- Never log the resolved value, only the variable name

---

## Registering an adapter

In your package's `pyproject.toml`:

```toml
[project.entry-points."harness.scanners"]
my_scanner = "my_package.scanners:MyScanner"

[project.entry-points."harness.audit_sinks"]
my_sink = "my_package.sinks:MySink"
```

After `pip install`, the adapter is available by name in `harness.yaml`:

```yaml
scan_input:
  enabled: true
  scanners:
    - name: my_scanner

audit_sinks:
  - name: my_sink
    config:
      endpoint: "https://..."
```

---

## Discovery and conflict detection

`adapters/discovery.py` loads all entry points for a group on first access and caches them. If two packages register the same name under the same group, `AdapterDiscoveryError` is raised at startup with both class paths listed. Name collisions are never silently resolved.

---

## Testing your adapter

Implement the relevant contract test suite. Every adapter must pass all tests in its group's contract file:

| Group | Contract file |
|---|---|
| scanners | `tests/contracts/test_scanner_contract.py` |
| audit_sinks | `tests/contracts/test_audit_sink_contract.py` |
| policy | `tests/contracts/test_policy_contract.py` |
| tool_registry | `tests/contracts/test_tool_registry_contract.py` |
| tool_sources | `tests/contracts/test_tool_sources_contract.py` |
| secrets | `tests/contracts/test_secrets_contract.py` |

Run the contract suite against your implementation by parameterising the fixtures.
