# Boundaries

Three boundaries surround every agent turn. Each emits exactly one `AuditEvent` per call regardless of outcome.

```
user text ──► scan_input ──► LLM ──► check_tool_call ──► tool ──► LLM ──► scan_output ──► response
```

---

## scan_input

**File:** `boundaries/scan_input.py` (delegates to `boundaries/_scan.py`)

Inspects the user's text before it reaches the LLM.

| Behaviour | Detail |
|---|---|
| Disabled | Emits `AuditEvent(disabled=True, decision=allow)`. Returns `ScanVerdict(blocked=False)`. |
| Scanners run | Concurrently via `asyncio.gather`. Exceptions per-scanner are logged and treated as empty findings — pipeline continues. |
| Block threshold | Configurable `block_at` severity (default `high`). Any finding at or above this level sets `blocked=True`. |
| Redaction | If any scanner returns `redacted_text`, the last one wins. Callers should use `verdict.redacted_text or original_text`. |

**Return type:** `ScanVerdict`

```python
verdict = await harness.scan_input(user_text, ctx)
if verdict.blocked:
    return "Input rejected"
safe_text = verdict.redacted_text or user_text
```

---

## check_tool_call

**File:** `boundaries/check_tool_call.py`

The mandatory gate — cannot be disabled. Four layers in strict order. First deny anywhere wins.

### Layer 1a — agent registered?

`AgentRegistry.get(ctx.agent_id)` raises `AgentNotRegisteredError` if the agent was never loaded. Returns `GateDecision(allowed=False)`.

### Layer 1b — allowed_tool_names

Hard pre-policy gate. `tool_name` must be in `AgentConfig.allowed_tool_names` (or `SubAgentConfig.allowed_tool_names` for subagent calls). Policy cannot override this.

### Layer 1c — allowed_tags (subagent capability gate)

Only active when `ctx.allowed_tags is not None` (i.e. this is a subagent call). Every tag on the tool must be in `allowed_tags`. Prevents a subagent from calling tools that require capabilities its parent never granted.

### Layer 2 — intersection policy

`PolicyEngine.evaluate(tool, args, ctx, rules=combined_rules)`.

`combined_rules` = subagent rules + parent rules. The engine evaluates these first, then its own global rules. First match wins. Default allow on no match.

### Layer 3 — arg scanning (optional)

Only fires for tools tagged with a tag in `scan_args_for_tags` (default: `["sensitive"]`). Runs configured `arg_scanners` on the flattened args text. Any finding at `HIGH` or above denies the call.

**Return type:** `GateDecision`

```python
gate = await harness.check_tool_call(tool_name, args, ctx)
if not gate.allowed:
    return f"Denied: {gate.deny_reason}"
effective_args = gate.redacted_args or args
result = await dispatch(tool_name, effective_args)
```

---

## scan_output

**File:** `boundaries/scan_output.py` (delegates to `boundaries/_scan.py`)

Identical structure to `scan_input`. Inspects the LLM's response before it reaches the user.

```python
verdict = await harness.scan_output(llm_response, ctx)
return verdict.redacted_text or llm_response
```

---

## Audit invariants

These hold on every code path, including error and disabled paths:

- Exactly **one** `AuditEvent` per boundary call.
- Disabled boundary → `decision=allow`, `disabled=True`, `finding_count=0`.
- `decision=deny` → `deny_reason` is non-null.
- `decision=blocked` → only on `input_scan` or `output_scan`.
- `decision=deny` → only on `tool_call_gate`.
- `tenant_id` is stamped from `HarnessConfig`, never from the caller.
