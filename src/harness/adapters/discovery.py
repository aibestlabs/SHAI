# harness/adapters/discovery.py — adapter resolution via Python entry points.
#
# RESPONSIBILITY
#   Resolve adapter NAMES (as written in harness.yaml) to adapter CLASSES
#   (registered by some installed package). This is the load-bearing
#   mechanism that makes the three-package layout work:
#     - `harness` registers reference adapters under groups like
#       "harness.scanners", "harness.policy", etc.
#     - `harness-enterprise` registers production adapters under the
#       SAME groups.
#     - A customer's own package can register under the same groups and
#       be picked up without any harness code change.
#
# WHAT TO IMPLEMENT
#   - GROUP_NAMES: a frozenset of the five canonical entry-point group
#     strings:
#       harness.scanners
#       harness.policy
#       harness.audit_sinks
#       harness.tool_registry
#       harness.secrets
#
#   - resolve(group: str, name: str) -> type
#       Look up `name` in entry-point group `group`. Returns the class
#       (not an instance). Raises AdapterDiscoveryError with context
#       (group, name, list of names currently registered in that group)
#       on miss.
#
#   - list_registered(group: str) -> list[str]
#       Enumerate all names registered under a group. Used by the CLI's
#       `harness adapters list` and by AdapterDiscoveryError to give a
#       helpful error message.
#
#   - Implementation uses importlib.metadata.entry_points(group=...).
#     Cache the lookup at module load — entry points don't change at
#     runtime. The cache is module-level; no need for an explicit
#     refresh API (restart the process).
#
# INVARIANTS
#   - Resolution is by NAME, never by class import path. Customers
#     should never have to write "harness_enterprise.scanners.purview:Purview"
#     in their config — just "purview".
#   - Name collisions across packages are detected at discovery time.
#     If two packages register the same name under the same group,
#     raise AdapterDiscoveryError at the first list/resolve call.
#     Don't silently pick one.
#
# DO NOT
#   - Allow dotted-path fallback (importlib.import_module of an arbitrary
#     string from config). Entry points are the only registration path.
#     This is what lets the customer audit which adapters are installed.
#   - Reload entry points on demand. Restart-to-change.
#   - Hide AdapterDiscoveryError behind a default. A typo in harness.yaml
#     must FAIL LOUDLY at startup, not silently use a reference adapter.
