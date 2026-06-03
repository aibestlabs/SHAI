# harness/config/schema.py — the harness.yaml schema.
#
# RESPONSIBILITY
#   Define the pydantic models that validate a parsed harness.yaml.
#   Source of truth for what a valid harness configuration looks like.
#   Every field maps to a real call site in the codebase.
#
# WHAT TO IMPLEMENT
#   - AdapterRef:
#       name:   str
#       config: dict[str, Any] = {}
#
#   - ToolSourceConfig:
#       name:        str
#       transport:   Transport           (local | mcp | skill)
#       tags:        list[str]
#       tools:       list[str]           (skill only; non-empty required)
#       url:         str | None          (mcp only; non-empty required)
#       credentials: dict[str, str] = {} (mcp only; values are secret:// refs)
#       config:      dict[str, Any] = {}
#
#   - BoundaryConfig:
#       enabled:   bool = True
#       block_at:  Severity = Severity.high
#       scanners:  list[AdapterRef] = []
#       (scanners non-empty required when enabled=True)
#
#   - ToolCallGateConfig:
#       arg_scanners:        list[AdapterRef] = []
#       scan_args_for_tags:  list[str] = ["sensitive"]
#
#   - AgentsConfig:
#       directory: str | None   (informational only; not watched)
#
#   - LoggingConfig:
#       level: str = "INFO"
#       json:  bool = True
#
#   - HarnessConfig (root, extra="forbid"):
#       version:          int = 1
#       scan_input:       BoundaryConfig
#       check_tool_call:  ToolCallGateConfig
#       scan_output:      BoundaryConfig
#       policy:           AdapterRef               (required)
#       audit_sinks:      list[AdapterRef]          (required, min_length=1)
#       tool_registry:    AdapterRef = name="memory"
#       secrets:          AdapterRef = name="env"
#       tool_sources:     list[ToolSourceConfig] = []
#       agents:           AgentsConfig = AgentsConfig()
#       logging:          LoggingConfig
#
#   - Validators:
#       - audit_sinks non-empty
#       - scan_input.scanners non-empty when enabled=True
#       - scan_output.scanners non-empty when enabled=True
#       - ToolSourceConfig.tools non-empty when transport=skill
#       - ToolSourceConfig.url non-empty when transport=mcp
#
# DO NOT
#   - Add SandboxPolicyConfig — removed entirely.
#   - Add VerifierConfig — not part of core.
#   - Add IsolationMode — isolation is structural, not configurable.
#   - Add fields without a consumer in the codebase.
