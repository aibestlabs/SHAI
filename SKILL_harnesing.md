---
name: harnesing
description: "creating a harness"
---

# CLAUDE.md

This file is the canonical guide for AI assistants working in the `shai` repository.
Read it completely before making any change.

You are a senior software engineer. Understand the codebase deeply: its intent,
component relationships, and how operations behave across the system. Before
changing anything, inspect existing code and patterns, reuse what already exists,
and add only the smallest clean change needed. Never duplicate functionality,
over-engineer, or add code unless it is truly necessary.

---

## 0. NON-NEGOTIABLE: You must have the full codebase before writing any code

**NEVER write, modify, or propose code without first reading the actual files
you intend to change.** This rule has no exceptions.

Before any implementation session:
- Confirm the codebase has been shared (zip upload, git clone, or file-by-file)
- Read every file you plan to touch using the view or bash tool
- Read every file that imports from or is imported by the files you plan to touch
- If the codebase has not been shared, stop and ask for it

**Why this rule exists:** In a prior session, code was written without reading
the actual codebase. The result was a `RuntimeContext` dataclass that replaced
the existing `AgentContext` Pydantic model. Every boundary, the facade, all
integrations, and all tests import `AgentContext` — the replacement broke the
entire codebase. The rollback cost significant time. This will not happen again.

Common failure modes to avoid:
- Assuming a type name (`RuntimeContext`, `GateDecision`, `ScanVerdict`) based
  on prior conversations — always read the actual file first
- Writing stub implementations of files that already exist in production
  (e.g. writing a new `scanners_base.py` when `base.py` already has the
  production Scanner Protocol)
- Replacing a Pydantic model with a dataclass or vice versa without reading
  the type's full usage across the codebase
- Adding fields to a frozen Pydantic model without checking all its callsites

Backward compatibility framing (`extras`, `**kwargs`, "so existing code won't
break") is a signal you are not reading the codebase. This is a dev project —
there are no deployed callers. Change the real type directly after reading it.

---

## 1. What this project is

`shai` is a Python SDK that owns the **control plane** around an agent's
LLM loop. The agent — written by the customer, in whatever framework they
prefer — owns the loop itself. The harness governs the boundaries around it.

The public facade is `SHAI` (from `harness.core.harness`). Agents interact
with it through four per-turn methods after startup:

```python
harness = await SHAI.from_yaml("config/harness.yaml")
await harness.register_tools([...])
ctx = await harness.load_agent("config/agents/my_agent.yaml")

# Per turn:
verdict = await harness.scan_input(text, ctx)
gate    = await harness.check_tool_call(name, args, ctx)
result  = await source.call(name, gate.redacted_args or args)
verdict = await harness.scan_tool_result(result, ctx, tool_name=name)
verdict = await harness.scan_output(text, ctx)
```

Five security boundaries:

| Boundary | Method | Purpose |
|---|---|---|
| `input_scan` | `scan_input` | Catch injection/PII before LLM |
| `tool_call_gate` | `check_tool_call` | Gate tool calls — 4-layer check |
| `tool_result_scan` | `scan_tool_result` | Catch indirect injection in tool returns |
| `file_scan` | `scan_file` | Structural + content scan of uploaded files |
| `output_scan` | `scan_output` | Catch PII/exfiltration before response |

### What the harness is NOT

- No LLM client — never imports an LLM SDK
- No agent loop — does not own the turn lifecycle
- No memory primitives — memory is out of scope
- No response composition — the agent assembles its own output
- No tool execution — the harness gates; the agent dispatches

---

## 2. Core types — read before touching any of these files

These are the types that cross every boundary. Read their actual files before
changing anything that uses them.

### `AgentContext` (`src/harness/core/context.py`)

The identity envelope passed on every boundary call. **Pydantic BaseModel,
frozen=True.** Obtained from `harness.load_agent()` — never constructed
directly in agent code.

```python
class AgentContext(BaseModel, frozen=True):
    agent_id:        str               # which top-level agent
    sub_agent_id:    str | None = None # which subagent (if any)
    allowed_tags:    list[str] | None = None  # capability scope
    conversation_id: str | None = None # session key for threat accumulator
```

Key methods: `scope_subagent(sub_agent_id, *, allowed_tags)`, `to_log_fields()`.

`tenant_id` is **NOT** on `AgentContext` — it lives on `HarnessConfig` and is
stamped on `AuditEvent` directly by the SHAI facade.

### `Tool` (`src/harness/tools/tool.py`)

**Pydantic BaseModel, frozen=True.**

```python
class Tool(BaseModel, frozen=True):
    name:        str
    tags:        list[str]
    transport:   Transport   # LOCAL | MCP | SKILL
    description: str | None = None
```

The production `Tool` does **not** have `schema`, `cost_weight`,
`argument_rules`, or `irreversibility` fields. Read the file before adding
anything.

### `AuditEvent` (`src/harness/core/events.py`)

**Pydantic BaseModel, frozen=True.** Always constructed via `AuditEvent.build()`
— never constructed directly. Fields include `timestamp`, `boundary`,
`decision`, `tenant_id`, `agent_id`, `sub_agent_id`, `tool_name`, `transport`,
`adapters`, `finding_count`, `max_severity`, `deny_reason`, `audit_tags`,
`extra`, `signature`.

### `GateDecision` / `ScanVerdict` / `Finding` (`src/harness/core/verdicts.py`)

All **Pydantic BaseModel, frozen=True**. `GateDecision` has `allowed`,
`deny_reason`, `redacted_args`, `dispatch_token`, `source_name`.
`ScanVerdict` has `status: ScanStatus`, `findings`, `redacted_text` and
convenience properties `blocked` and `warned`. There is no `blocked: bool`
field — use `verdict.blocked` (property).

### Types (`src/harness/core/types.py`)

All `StrEnum`. Key enums: `BoundaryName`, `Decision`, `Severity`, `Transport`,
`ScanAction`, `ScanStatus`. There is no `ArgumentRule`, `Irreversibility`,
`Finding`, or `ScanVerdict` in `types.py` — those live in `verdicts.py`.

### Errors (`src/harness/core/errors.py`)

`HarnessError` base with structured context fields (`tenant_id`, `agent_id`,
`sub_agent_id`, `adapter`, `boundary`, `op`). Production subclasses:
`ConfigError`, `AdapterDiscoveryError`, `AgentNotRegisteredError`,
`AgentConflictError`, `SubAgentNotDeclaredError`, `ToolNotRegisteredError`,
`PolicyEvaluationError`, `AuditEmissionError`, `NetworkPolicyError`,
`MCPInvocationError`.

New error classes must follow the same constructor pattern. Check the file
before adding — the class may already exist under a different name.

---

## 3. Open-core packaging

Three sibling Python distributions:

| Package | Licence | Contents |
|---|---|---|
| `harness` | Apache-2.0 (or BSL) | Core, reference adapters, framework integrations |
| `harness-enterprise` | Commercial | Production adapters: DLP, SIEM, OPA/Cedar, Vault, central registry |
| `harness-cli` | Apache-2.0 | `harness validate`, `harness policy test`, `harness audit replay` |

Hard rules:
- `harness` may not import from `harness-enterprise`
- `harness-enterprise` may not add new public API visible to agent code
- Every adapter passes the same contract suite regardless of package

---

## 4. Architecture

### 4.1 Repository layout

```
src/harness/
├── __init__.py              public exports: SHAI, Tool, AgentContext, verdicts, types, errors
├── core/
│   ├── harness.py           SHAI facade — the only public entry point
│   ├── context.py           AgentContext (Pydantic, frozen)
│   ├── types.py             StrEnums: BoundaryName, Decision, Severity, Transport, ScanAction, ScanStatus
│   ├── verdicts.py          GateDecision, ScanVerdict, Finding (Pydantic, frozen)
│   ├── events.py            AuditEvent + AuditEvent.build() + now_ms()
│   ├── errors.py            HarnessError hierarchy
│   ├── normalize.py         canonicalize() — multi-view normalization pipeline
│   └── budget_store.py      (legacy — SessionBudget lives in boundaries/session_budget.py)
├── tools/
│   ├── tool.py              Tool (Pydantic, frozen) — name, tags, transport, description
│   ├── registry.py          ToolRegistry — async register/get/list/as_dict
│   └── source.py            LocalSource, MCPSource, SkillSource, SourceRegistry, ToolSource
├── boundaries/
│   ├── check_tool_call.py   4-layer gate: allowed_tool_names → tags → policy → arg scan
│   ├── _scan.py             run_scan(), run_file_scan(), run_tool_result_scan() — shared pipeline
│   ├── session_budget.py    SessionBudget, ExecutionLimits — DoS/unbounded consumption controls
│   └── session_accumulator.py  ThreatAccumulator — multi-turn threat tracking
├── agents/
│   ├── agent_config.py      AgentConfig, SubAgentConfig, RuleConfig (Pydantic)
│   └── registry.py          AgentRegistry
├── adapters/
│   ├── scanners/
│   │   ├── base.py          Scanner Protocol (async), ScanResult
│   │   ├── regex_pii.py     RegexPIIScanner
│   │   ├── injection_scan.py InjectionScanner
│   │   ├── jailbreak_scan.py JailbreakScanner
│   │   ├── identity_spoof_scan.py  IdentitySpoofScanner
│   │   ├── mcp_metadata_scanner.py MCPMetadataScanner
│   │   ├── rate_limiter.py  RateLimiter
│   │   ├── file_scanner.py  FileScanner (structural + content)
│   │   └── l10n/            pattern YAML files
│   ├── audit_sinks/
│   │   ├── stdout.py        StdoutSink
│   │   └── file.py          FileSink (rotating JSONL)
│   ├── secrets/
│   │   └── env.py           EnvVarProvider
│   └── discovery.py         entry-point adapter resolution
├── audit/
│   └── emitter.py           AuditEmitter, AuditSink Protocol
├── policy/
│   ├── engine.py            PolicyEngine Protocol, PolicyDecision
│   └── rules.py             RuleBasedPolicy
├── config/
│   ├── schema.py            HarnessConfig, SourceConfig, ExecutionBudgetConfig (Pydantic)
│   └── loader.py            load_yaml() with secret resolution
├── integrations/
│   ├── base.py              ShaiTool, @shai_tool decorator
│   ├── langchain.py
│   ├── langgraph.py
│   ├── crewai.py
│   ├── pydantic_ai.py
│   ├── openai_agents.py
│   └── anthropic_sdk.py
└── connectivity/
    ├── token.py             DispatchToken, sign_token(), encode_token()
    ├── transport.py         ShaiTransport (httpx-based, validates dispatch tokens)
    └── config.py            ConnectivityConfig
```

### 4.2 check_tool_call gate — 4 layers in strict order

```
Layer 1: tool name in agent's allowed_tool_names?         hard gate
Layer 2: tool.tags ⊆ ctx.allowed_tags?                    subagent capability gate
Layer 3: intersection policy (subagent ∩ parent ∩ global) RuleBasedPolicy
Layer 4: optional arg scanning for tools tagged 'sensitive'
```

Each layer fails closed. Exactly one `AuditEvent` is emitted per call via
`AuditEvent.build()`. The gate never dispatches the tool.

The SHAI facade wraps `run_gate()` and adds: rate limiting (before the gate),
session execution budget (before the gate), dispatch token issuance (after allow).

### 4.3 Scanner Protocol

All scanners are **async**:

```python
class Scanner(Protocol):
    name: str
    async def scan(self, text: str, ctx: AgentContext) -> ScanResult: ...
```

`ScanResult` is internal: `findings: list[Finding]`, `redacted_text: str | None`.
Scanners never emit audit events — that is `run_scan()`'s job.

### 4.4 Session budget (DoS controls)

`SessionBudget` in `boundaries/session_budget.py` — called by the SHAI facade
in `check_tool_call` before the gate runs. Four controls:

1. Step counter — total tool calls per session (`max_steps`)
2. Token burn-down — cumulative tokens (`max_tokens_per_session`)
3. Per-prompt fan-out — tool calls per user turn (`max_tool_calls_per_prompt`)
4. Loop detection — Jaccard similarity on (tool, args) fingerprints

`ExecutionLimits` carries the per-agent config (merged from global
`execution_budget` in `harness.yaml` and per-agent `limits:` in
`agent-xx.yaml`).

### 4.5 Audit pipeline

Every boundary call emits exactly one `AuditEvent` regardless of outcome.
Emission is structural — if a boundary returns without calling
`emitter.emit()`, the test suite catches it. `AuditEvent` never stores raw
text, full argument payloads, matched substrings, or LLM responses.

---

## 5. Absolute design constraints

### Before making any change

1. Read the files you plan to change with view or bash tool
2. Read every file that imports from those files
3. Read the existing test file for the module you are changing
4. Determine whether the feature already exists under a different name
5. Identify all callsites of any type or function you plan to modify

### No backward-compatibility patterns

This is a dev project. There are no deployed callers, no older versions,
no running systems. Do not:
- Use `extras`, `**kwargs`, or untyped dicts to avoid changing a signature
- Add optional fields to dodge a type change
- Preserve old code paths alongside new ones
- Write "so existing code won't break" in a comment

If a signature needs to change, change it directly after reading all callsites.

### Mandatory execution stance

- Do not over-engineer
- Simplify before extending when the topology is confusing
- Prefer direct code over indirection
- Keep public surfaces small and sharp
- Avoid parallel paths for the same behavior
- Prefer extending canonical paths over creating alternate execution paths

### Code style

- One responsibility per module
- Explicit, direct code over cleverness
- No thin wrappers that only forward data
- No abstractions unless they remove real duplication
- Logs only where they pay for themselves (start/end of operations, error
  context, key counters)

### Pydantic vs dataclass

Production types (`AgentContext`, `Tool`, `AuditEvent`, `GateDecision`,
`ScanVerdict`, `Finding`, `AgentConfig`, `HarnessConfig`) are **Pydantic
BaseModel, frozen=True**. Never replace a Pydantic model with a dataclass.
Never replace a Pydantic model with a different Pydantic model without reading
all callsites first.

### Error handling

- Never swallow exceptions silently in core flows
- Always log with enough context: `agent_id`, `boundary`, relevant IDs
- Keep error handling close to the boundary where recovery is meaningful
- Do not add defensive catch-all logic that hides broken invariants

### Logging field names

Use these across all modules:
- `agent_id`, `sub_agent_id` — from `AgentContext.to_log_fields()`
- `boundary` — one of the `BoundaryName` values
- `decision` — one of the `Decision` values
- `adapter` — the adapter name as registered
- `finding_count`, `severity` — for scan results
- `op` — the operation name for non-boundary code paths

### One canonical path per boundary

`_scan.py`, `check_tool_call.py` each have exactly one implementation.
No parallel "experimental" or "v2" variants. Change the existing file.

### The facade is the only public surface

`SHAI`, `Tool`, `AgentContext`, `AgentConfig`, `SubAgentConfig`, `RuleConfig`,
`ScanVerdict`, `GateDecision`, `Finding`, error classes, and type enums are
the entire public API. Everything else is internal.

### Configuration over code

Behavior changes belong in `harness.yaml` or `agent-xx.yaml`, not constructor
arguments or method overrides.

### No silent disable

When a boundary is configured as disabled, it still runs and emits an audit
event marked `disabled=true`. A disabled boundary is observable; a missing
boundary is not.

### Audit emission is structural

Boundary code that returns without emitting an audit event is broken. The
test suite enforces this.

### Test the contract, not the implementation

`tests/contracts/` defines what every adapter must do. Reference adapters
and production adapters run the same suite.

---

## 6. Where to look first

- `docs/architecture.md` — full architecture
- `docs/boundaries.md` — per-boundary contracts
- `docs/adapters.md` — how to write a new adapter
- `docs/audit-schema.md` — AuditEvent schema field by field
- `examples/hand_rolled_loop.py` — canonical usage reference
- `harness.yaml.example` — canonical config reference
- `.claude/skills/` — in-repo skills covering specific subsystems
