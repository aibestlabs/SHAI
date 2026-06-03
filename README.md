# harness

Control-plane SDK for production agents. Three security boundaries around the
LLM loop — `scan_input`, `check_tool_call`, `scan_output` — plus always-on
structured audit. The agent owns the loop; the harness governs the boundaries.

## Read this first

- `CLAUDE.md` — design rules and contributor guide. Read before changing code.
- `docs/architecture.md` — full folder tree with per-file responsibilities.
- `docs/boundaries.md` — boundary contracts: inputs, outputs, audit events.
- `examples/hand_rolled_loop.py` — canonical reference for using the SDK.
- `harness.yaml.example` — canonical reference configuration.

## Install

```
pip install harness
```

Reference adapters are bundled. For production-grade DLP, SIEM, policy and
secrets adapters, install `harness-enterprise` separately.
