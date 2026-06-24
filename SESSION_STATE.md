# SHAI Session State
*Last updated: 2026-06-23 — end of active dev session*

---

## What is SHAI

**Secure Harness AI** — a Python SDK that acts as a security control plane between agent code and tool dispatch. One `SHAI` instance per deployment, shared across multiple concurrent agents and turns.

```
user text → scan_input → LLM → check_tool_call → tool → scan_tool_result → LLM → scan_output → response
```

Package name: `shai`. Python package: `harness`. Install: `pip install shai` (MCP: `pip install shai[mcp]`). CLI: `shai validate / agents list / audit tail`.

---

## Repository layout

```
/home/claude/harness/
├── src/harness/              ← main package
│   ├── core/
│   │   ├── harness.py        ← SHAI facade (single public entry point)
│   │   ├── context.py        ← AgentContext
│   │   ├── events.py         ← AuditEvent
│   │   ├── verdicts.py       ← ScanVerdict (status: ScanStatus), GateDecision, Finding
│   │   ├── types.py          ← BoundaryName, Decision, ScanAction, ScanStatus, Severity, Transport
│   │   └── errors.py         ← full exception hierarchy
│   ├── boundaries/
│   │   ├── _scan.py          ← shared scan pipeline (block/alert/redact action logic)
│   │   └── check_tool_call.py← four-layer gate (L1 name, L2 tags, L3 policy, L4 arg scan)
│   ├── agents/
│   │   ├── agent_config.py   ← AgentConfig, SubAgentConfig, RuleConfig
│   │   └── registry.py       ← AgentRegistry
│   ├── tools/
│   │   ├── tool.py           ← Tool descriptor
│   │   ├── registry.py       ← ToolRegistry
│   │   └── source.py         ← ToolSource Protocol, SourceRegistry, LocalSource, SkillSource, MCPSource
│   ├── policy/
│   │   ├── engine.py         ← PolicyEngine Protocol
│   │   └── rules.py          ← RuleBasedPolicy (inline YAML rules, no external file)
│   ├── audit/
│   │   └── emitter.py        ← AuditEmitter (fan-out + optional HMAC-SHA256 signing)
│   ├── config/
│   │   ├── schema.py         ← HarnessConfig, SourceConfig, BoundaryConfig, PolicyConfig, etc.
│   │   └── loader.py         ← load_yaml (env-var + secret:// resolution)
│   ├── adapters/
│   │   ├── scanners/
│   │   │   ├── regex_pii.py          ← PII + credential scanner (7 categories)
│   │   │   ├── injection_scan.py     ← YAML-rule injection scanner
│   │   │   ├── file_scanner.py       ← structural file scanner
│   │   │   ├── rate_limiter.py       ← sliding-window token bucket
│   │   │   ├── injection_patterns.yaml   ← 17-rule catalog
│   │   │   └── patterns_for_doc.yaml     ← 9-rule catalog (tool results)
│   │   ├── audit_sinks/
│   │   │   ├── stdout.py     ← StdoutSink (JSONL)
│   │   │   └── file.py       ← FileSink (rotating JSONL)
│   │   ├── secrets/
│   │   │   └── env.py        ← EnvVarProvider, Secret, resolve_secret_uri
│   │   └── discovery.py      ← entry-point discovery + caching
│   ├── integrations/
│   │   ├── anthropic_sdk.py, langgraph.py, langchain.py
│   │   ├── crewai.py, pydantic_ai.py, openai_agents.py
│   │   └── HarnessToolNode  ← LangGraph: gate + dispatch + scan_tool_result
│   └── py.typed              ← PEP 561 marker
├── src/harness_cli/          ← CLI (shai validate / agents list / audit tail)
├── tests/
│   ├── unit/ (18 files)
│   ├── integration/ (3 files)
│   ├── contracts/ (10 files)
│   ├── security/ (2 files)
│   └── perf/ (2 files)
├── config/
│   ├── harness.yaml          ← example operator config
│   ├── agents/orchestrator_agent.yaml
│   └── agents/research_agent.yaml
├── examples/
│   ├── shai_demo.py          ← 10-scenario security demo (no external deps)
│   └── langgraph_agent.py    ← LangGraph + Ollama (qwen2.5:3b) working example
├── docs/ (9 files)
├── ARCHITECTURE.md
├── README.md
├── pyproject.toml
└── harness.yaml.example
```

---

## Key architecture decisions

**`SHAI.from_yaml()` is async** — builds SourceRegistry, constructs MCPSource/LocalSource objects, resolves secrets.

**`policy` is inline** — `harness.yaml` contains `policy: rules: [...]` directly. No separate `rules.yaml`. Same schema as agent-level `policy_rules`.

**`ScanVerdict` uses `status: ScanStatus`** — not `blocked: bool`. `ScanStatus = ALLOW | WARN | BLOCK`. `verdict.blocked` and `verdict.warned` exist as read-only properties for convenience.

**Three scan actions** — `block` (hard stop), `alert` (pass through, emit WARN audit event), `redact` (replace PII with placeholder, pass through). Configurable per-boundary and per-scanner.

**Source tag overrides are per-agent** — `_source_overrides: dict[agent_id, dict[tool_name, Tool]]` in SHAI. When a source merges tags onto a tool that conflicts with the registry, the enriched variant is stored as a per-agent override. `_resolve_tools()` applies overrides on top of registry entries. Other agents are unaffected.

**Source `required: bool = True`** — default fail-safe. Missing or failed required source raises `ConfigError` at `load_agent()` time. `required: false` logs and skips. Policy-suppressed sources always skip (intentional, not failure).

**Transport enum is meaningful** — `LOCAL`/`SKILL` = Python callable in process. `MCP` = call `source.call(name, args)` via MCPSource after gate.

**No `rules_path`** — `RuleBasedPolicy` takes a `rules: list[RuleConfig]` directly. The external rules file pattern was removed.

---

## Schema quick reference

```yaml
version: 1
tenant_id: "my-deployment"

scan_input:
  enabled: true
  block_at: high
  action: block          # block | alert | redact
  scanners:
    - name: regex_pii
      action: redact     # per-scanner override
      redact_with: "***"
    - name: injection_scan
      action: block

scan_output:
  enabled: true
  block_at: high
  action: block
  scanners:
    - name: regex_pii

scan_tool_result:
  enabled: true
  block_at: high
  action: block

scan_file:
  enabled: false
  block_at: high
  action: block
  max_size_mb: 50

check_tool_call:
  rate_limit:
    enabled: true
    window_seconds: 60
    max_calls_per_window: 60
    max_calls_per_tool: 20
  arg_scanners:
    - name: regex_pii
  scan_args_for_tags:
    - sensitive

policy:
  rules:
    - id: allow_local
      match:
        transport: [local, skill]
      action: allow
    - id: deny_mcp_default
      match:
        transport: [mcp]
      action: deny
      reason: "MCP requires explicit agent-level allow rule"

audit_sinks:
  - name: file
    config:
      path: ./logs/audit.jsonl
  - name: stdout

audit_signing:
  enabled: false
  secret: "secret://AUDIT_SIGNING_KEY"

sources:
  - name: slack_mcp
    transport: mcp
    url: "https://mcp.slack.com/sse"
    credentials:
      token: "secret://SLACK_MCP_TOKEN"
    tags: [external_mcp, messaging]
    required: true        # fail-safe default
  - name: analytics
    transport: mcp
    url: "https://analytics.internal/sse"
    required: false       # optional — failure skips, not fatal
```

---

## OWASP Agentic AI Threats coverage

| Threat | Coverage | Controls |
|---|---|---|
| T1 Goal Hijacking | Partial | InjectionScanner, L1 hard gate |
| T2 Tool Misuse | Full | L1 name gate, L2 tag gate, L3 policy, rate limiter |
| T3 Uncontrolled Actions | Full | L1-L3 gates, subagent scoping, source suppression |
| T4 Resource Overload | Full | Sliding-window rate limiter (global + per-tool) |
| T5 Prompt Injection | Full | InjectionScanner 17-rule catalog |
| T6 Indirect Injection | Full | scan_tool_result with patterns_for_doc.yaml |
| T8 Repudiation | Full | HMAC-SHA256 signed audit events |
| T9 Privilege Escalation | Full | Subagent capability gate, policy intersection |
| T11 Sensitive Data Exposure | Full | RegexPII (7 categories incl. secret.credential) + arg scan |
| T16 Data Exfiltration | Partial | RegexPII on output; network-layer planned (shai-connectivity) |
| T17 Supply Chain | Partial | FileScanner, source suppression, secret resolution |

---

## Completed work (this session)

### Core architecture
- `SHAI` facade (renamed from `Harness`) — async `from_yaml()`, full wiring
- Four-layer gate (`check_tool_call`) with pre-gate, L1-L4
- All four scan boundaries + `scan_tool_result` (R2)
- `SourceRegistry` fully wired — `LocalSource`, `SkillSource`, `MCPSource`
- Per-agent source tag overrides (`_source_overrides`)
- Source `required` flag — fail-safe default

### Security (P1 complete)
- R1: Rate limiter (sliding-window, per-agent global + per-tool)
- R2: Tool result scanning (indirect injection)
- R3: Audit event HMAC-SHA256 signing
- R4/R5: Removed (explained in session transcripts)

### Scan actions
- `block` / `alert` / `redact` on each boundary
- Per-scanner action + `redact_with` override on `AdapterRef`
- `ScanStatus` enum replacing `blocked: bool`
- `Decision.WARN` for alert path

### Schema cleanup
- Removed: `allowed_extensions`, `tool_registry`, `secrets`, `agents.directory`, `tool_sources`, `logging`, `rules_path`
- Inline policy: `PolicyConfig.rules: list[dict]` → `parsed_rules()` → `RuleBasedPolicy`
- `audit_sinks` optional (default stdout)

### Package readiness
- `py.typed` marker added
- `version("shai")` fixed in `__init__.py`
- All missing exports added to `__init__.py`
- YAML pattern files in wheel (`artifacts`)
- `sdist` includes documented
- CLI `prog="shai"` aligned with entry point

### Examples
- `shai_demo.py` — 10 scenarios, loads `config/harness.yaml` + `config/agents/orchestrator_agent.yaml`
- `langgraph_agent.py` — LangGraph + Ollama (qwen2.5:3b), `HarnessToolNode` with full gate + `scan_tool_result`

### Docs
- `README.md` — full rewrite with OWASP table, scanner descriptions, perf budget
- `ARCHITECTURE.md` — new file, complete component map
- All `docs/*.md` rewritten from code (not from stale descriptions)

---

## Known gaps / planned work

### shai-connectivity (architecture defined, Phase 1 next)

Full architecture documented in `docs/connectivity.md`. Five phases:

**Phase 1 (next):** Token issuance in SHAI harness — `DispatchToken` dataclass,
`GateDecision.dispatch_token` field, `connectivity:` block in `HarnessConfig`,
`allowed_urls`/`allowed_methods` on `SourceConfig`. Harness-only changes.

**Phase 2:** `shai-gateway` — HTTP/HTTPS sidecar proxy, token validation,
nonce store, `NetworkAuditEvent` emission, configurable no-token policy.

**Phase 3:** L7 policy in gateway — YAML rules per source/agent/subagent, hot-reload.

**Phase 4:** `shai-inference-router` — LLM credential isolation, model allowlist
per agent, per-agent token/request rate limits.

**Phase 5:** eBPF/netfilter enforcement — raw socket interception for
higher-assurance deployments.

OWASP threats closed when complete: T16 (full), T17 (full), credential
exfiltration (inference router), cross-agent traffic (netns isolation).

### MCPSource integration tests
`MCPSource` is unit-tested with mocks only. No test against a live MCP server. The SSE connection, JSON-RPC handshake, and tool invocation path are exercised only in `examples/langgraph_agent.py` against a real Ollama endpoint.

### Enterprise providers
`SecretsProvider` ABC has only `EnvVarProvider`. Vault, AWS KMS, GCP Secret Manager are out of scope for 0.1.x. Swap by replacing `EnvVarProvider()` in `from_yaml()`.

### P2 security items (from original security plan)
- R6: MCP metadata scanning — scan tool descriptions from MCP servers for injection before surfacing to LLM. Depends on MCPSource being wired (now done), so this is unblocked.
- R7: LLM consistency checker — enterprise-only, deferred.


### [0.2.x] shai-connectors — connector manifests for cloud services

**Problem.** Thousands of community MCP servers exist for cloud services
(Slack, WhatsApp, Gmail, GitHub, Notion, Linear). Operators can use any of
them today via `MCPSource`. What they cannot get from community MCPs is:
correct tag assignments, pre-declared `allowed_urls` for the egress gateway,
pre-wired scan policies (which tools need `scan_tool_result`, which carry
`sensitive` data), and verified security posture. Every operator reinvents
this per connector.

**Approach — manifests, not implementations.** `shai-connectors` is a
curated registry of connector manifests — lightweight YAML files that wrap
an existing community MCP with SHAI-specific security configuration. SHAI
owns the manifest; the MCP server comes from the community or the service's
own hosted endpoint.

**Manifest format:**

```yaml
# connectors/slack.yaml
id: slack
display_name: "Slack"
categories: [communication, external]
mcp_server:
  type: remote
  image: "mcp/slack:latest"

allowed_urls:
  - "https://slack.com/api/*"
  - "https://edgeapi.slack.com/*"

tools:
  - name: send_message
    tags: [external_write, messaging]
    action: block
  - name: read_messages
    tags: [read, messaging]
    action: allow
  - name: react
    tags: [external_write, messaging]
    action: alert
  - name: search
    tags: [read, messaging]
    action: allow

scan_tool_result_on: [read_messages, search]

auth:
  type: token
  secret: "secret://SLACK_BOT_TOKEN"
```

**Usage in harness.yaml:**

```yaml
sources:
  - connector: slack           # loads manifest, wires everything
    credentials:
      token: "secret://SLACK_BOT_TOKEN"
    required: true
```

**Initial connector set:** Slack, WhatsApp, Gmail, GitHub, Notion, Linear,
Jira, Google Drive, Microsoft Teams.

**SHAI harness changes needed:**
- `SourceConfig` gains optional `connector: str` field that loads a manifest
  from the installed `shai-connectors` package
- `from_yaml()` resolves the manifest and merges it with any overrides in the
  source config
- `allowed_urls` from the manifest flows into the dispatch token when
  `connectivity.enabled`

**What this does not replace.** Operators who need custom tool names, custom
tags, or non-standard MCP servers still use the raw `sources:` config block.
Manifests are a convenience layer, not a constraint.

---

### [future] shai-local-connectors — local service MCP servers

**Design decision:** Local connector manifests are NOT shipped in `shai` core.
A manifest without its MCP server process is misleading — it loads cleanly
but fails at connection time. The manifest and the process must ship together.

**Package boundary:**
```
shai                  → ConnectorManifest model, load_manifest(), Tier A manifests
shai-local-connectors → local manifests + managed MCP server processes
```
`load_manifest()` will be extended to check `importlib.resources` entry points
registered by `shai-local-connectors`, giving a helpful install hint when a
local connector is requested but the package is not installed.

**Problem.** Locally-installed services (Apple Notes, Obsidian, local SQLite,
local filesystem) cannot use hosted MCP servers. They need a local MCP process
that talks to the service via local APIs or file paths.

**Approach.** Lightweight MCP servers — one per service — distributed as a
`shai-local-connectors` package. Each server exposes a small, well-defined
tool set with pre-wired SHAI tags.

**Initial local connector set:**

| Connector | Transport | Key tools | Tags |
|---|---|---|---|
| `apple-notes` | local MCP (macOS only) | `create_note`, `read_note`, `search_notes`, `list_folders` | `[read, write, local, notes]` |
| `obsidian` | local MCP | `read_note`, `write_note`, `search_vault`, `list_notes`, `append_note` | `[read, write, local, notes]` |
| `sqlite` | local MCP | `query`, `execute`, `list_tables`, `describe_table` | `[read, write, local, database]` |
| `filesystem` | local MCP | `read_file`, `write_file`, `list_dir`, `search_files` | `[read, write, local, filesystem]` |

**Security posture for local connectors:**
- `required: false` by default — local service absence should not crash startup
- `allowed_urls: []` — no outbound network calls permitted
- `filesystem` and `sqlite` connectors declare `allowed_paths` (analogous to
  `allowed_urls`) to scope read/write to declared directories or DB files
- All local connector tools carry `sensitive` tag by default — arg scanner
  fires on all calls

**Connector manifest (local):**

```yaml
# connectors/obsidian.yaml
id: obsidian
display_name: "Obsidian"
categories: [notes, local]
mcp_server:
  type: local
  package: "shai-local-connectors[obsidian]"
  command: "shai-obsidian-mcp"

allowed_urls: []          # no outbound network
allowed_paths:            # operator declares their vault path
  - "secret://OBSIDIAN_VAULT_PATH"

tools:
  - name: read_note
    tags: [read, local, notes]
    action: allow
  - name: write_note
    tags: [write, local, notes, sensitive]
    action: block
  - name: search_vault
    tags: [read, local, notes]
    action: allow
  - name: append_note
    tags: [write, local, notes, sensitive]
    action: alert

auth:
  type: none               # local filesystem access, no auth
```

**Scope (separate package, separate session):**
- `shai-filesystem-mcp`, `shai-sqlite-mcp`, `shai-obsidian-mcp`, `shai-apple-notes-mcp`
  (macOS only) — managed subprocess per connector
- `from_yaml()` spawns processes, manages lifecycle (start on `load_agent()`, stop on `close()`)
- `allowed_paths` field added to `SourceConfig` at that time — enforced at I/O level
- Entry point registration so `load_manifest('obsidian')` works after install
- Distributed as `pip install shai-local-connectors` with platform extras

---

### [0.2.x] Composite tool identity — (source_name, tool_name)

**Problem.** `ToolRegistry` is keyed by `tool_name` alone. Transport and
source tags are stamped on the `Tool` object at source activation time, not
at dispatch time. When two sources provide a tool with the same name (e.g.
a `LocalSource` and an `MCPSource` both expose `search_docs`), the registry
can only hold one variant. The `_source_overrides` per-agent dict partially
mitigates this — the last source to activate wins for that agent — but policy
rules that match on `transport: [mcp]` or `source_tags: [external_mcp]` will
fire or not based on activation order, not on which source the LLM's actual
call originated from.

**Current mitigation.** `ToolRegistry` raises `ConfigError` on same-name
conflict at `load_agent()` time, surfacing the ambiguity at startup rather
than silently at gate time. Operators who name tools distinctly per source
are not affected.

**Correct fix.** Tool identity at the agent resolution layer should be
`(source_name, tool_name)`. The gate receives this composite key, evaluates
policy against the source-specific `Tool` object, and ambiguity is
eliminated. The LLM still calls `search_docs`; the harness resolves it to
`("docs_local", "search_docs")` or `("slack_mcp", "search_docs")` based on
which source is active for the agent. `GateDecision` and dispatch routing
would carry the resolved source name.

**Scope.** Affects `check_tool_call` call sites, `GateDecision`,
`_agent_tools` dict structure, and how dispatch is routed. 0.2.x design
change. Document in `docs/sources.md` before implementing.

### `regex_pii` `secret.api_key` threshold
Currently 32+ chars. Discussed lowering to 16 for UUIDs/short keys. Not yet implemented.

---

## How to pick up in a new session

1. Read this file first.
2. Check `/mnt/transcripts/journal.txt` for session summaries.
3. Run `cd /home/claude/harness && python3 -m pytest tests/ -x -q` to see current test state.
4. The live codebase is at `/home/claude/harness/` — all source, tests, configs, examples.
5. The most recent full-sync zip in `/mnt/user-data/outputs/` is `harness-full-sync.zip` (note: may be slightly behind — the live codebase is authoritative).

---

## Running the project locally

```bash
# Install
cd harness
pip install -e ".[dev]"

# Run demo (no external deps)
python examples/shai_demo.py

# Run LangGraph agent (requires Ollama with qwen2.5:3b)
pip install langgraph langchain-ollama langchain-core
python examples/langgraph_agent.py

# Run tests
pytest
pytest tests/unit/
pytest tests/security/
pytest tests/perf/ -v -s   # prints timings

# CLI
shai validate --config config/harness.yaml
shai audit tail --file logs/audit.jsonl --follow
```

---

## Test fixtures

```
tests/fixtures/harness.yaml              ← minimal disabled-boundaries config
tests/fixtures/agents/orchestrator_agent.yaml  ← tools: search_docs, send_email, list_inbox
tests/fixtures/agents/research_agent.yaml      ← tools: search_docs only
```

No sources declared in fixtures — tests register tools directly via `register_tools()`.

---

## File tree of transcripts

```
/mnt/transcripts/
├── 2026-06-22-09-13-32-shai-harness-architecture-dev.txt
├── 2026-06-22-11-35-41-shai-harness-dev-session.txt
├── 2026-06-22-14-52-51-shai-harness-dev-session.txt
├── 2026-06-23-09-42-13-shai-harness-dev-session.txt
├── 2026-06-23-11-20-52-shai-harness-dev-session.txt
└── journal.txt
```
