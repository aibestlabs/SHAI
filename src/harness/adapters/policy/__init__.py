# harness/adapters/policy/__init__.py
#
# Package marker. The PolicyEngine Protocol lives in
# harness/policy/engine.py (canonical location, since the type is used
# by both the gate boundary and the adapter system). The reference
# rule-based engine lives in harness/policy/rules.py.
#
# This directory exists for parity with other adapter kinds and as the
# entry-point group root for `harness.policy`. New built-in policy
# engines (if any) live here; production engines (OPA, Cedar) live in
# harness-enterprise.
