# harness/boundaries/__init__.py
#
# RESPONSIBILITY
#   Package marker. May host a small private helper shared by scan_input
#   and scan_output (the two scan boundaries are structurally identical
#   except for which scanner set they use).
#
# WHAT TO IMPLEMENT (if needed)
#   - If scan_input.run and scan_output.run end up duplicating the
#     scanner-loop + finding-aggregation + verdict-assembly logic,
#     extract a private helper here (e.g. `_run_scan_pipeline(...)`).
#     The two boundary files then become thin wrappers that pass their
#     boundary name and scanner set to the helper.
#   - Do this ONLY when the duplication is real and structural — do not
#     pre-emptively factor before the second file exists. See CLAUDE.md
#     §5 "Code style."
#
# DO NOT
#   - Re-export boundary entry points. Callers (the facade) import from
#     the specific module.
#   - Put check_tool_call logic in a shared helper — its shape is
#     different (registry lookup + policy eval) and folding it together
#     would obscure the canonical path for the core gate.
