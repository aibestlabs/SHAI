# harness/core/__init__.py
#
# RESPONSIBILITY
#   Internal package marker. The public API surface is re-exported by the
#   top-level harness/__init__.py — do not re-export from here.
#
# DO NOT
#   - Add convenience re-exports. Make callers import from the specific
#     module (e.g. `from harness.core.verdicts import ScanVerdict`) so
#     dependencies between modules stay grep-visible.
