# Writing an adapter

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

The end-to-end recipe for adding a new adapter to any of the five
kinds, written so a third-party can publish their own package without
reading the source.

Sections:

1. **Pick a kind** — short tour of the five Protocols (Scanner,
   PolicyEngine, AuditSink, ToolRegistry, SecretsProvider) and what
   each is for.
2. **Implement the Protocol** — point at the canonical Protocol file
   (e.g. `harness/adapters/scanners/base.py`), show a minimal stub
   that satisfies the interface.
3. **Register under an entry point** — concrete `pyproject.toml`
   snippet showing how to register under the right group. Stress
   that names must be unique within a group across all installed
   packages.
4. **Pass the contract suite** — explain how to import the
   `tests/contracts/<kind>_contract.py` class, subclass it, and run
   pytest. The suite is the conformance gate; failing it means the
   adapter is non-conformant.
5. **Reference in harness.yaml** — show the YAML snippet that
   activates the adapter by name and passes constructor config.
6. **Logging and errors** — adapters use the standard logger; failure
   modes raise the exception types from `harness.core.errors` with
   the canonical context fields.

## What does NOT go here

- Production-adapter how-tos (Purview setup, OPA bundle layout). Those
  live in `harness-enterprise/docs/runbooks/`.
