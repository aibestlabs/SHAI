# harness/adapters/policy/base.py — Protocol re-export for symmetry.
#
# RESPONSIBILITY
#   Re-export PolicyEngine from its canonical location (harness/policy/engine.py)
#   so adapter authors discovering the codebase via adapters/<kind>/base.py
#   land on the right type. ONE LINE. No logic.
#
# WHAT TO IMPLEMENT
#   from harness.policy.engine import PolicyEngine  # noqa: F401
#
# DO NOT
#   - Restate or duplicate the Protocol here. The canonical definition
#     lives in harness/policy/engine.py.
#   - Add helper functions, base classes, or mixins. The Protocol is
#     all that is needed.
