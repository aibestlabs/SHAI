# Policy engine

PLACEHOLDER FOR THE CODING AGENT.

## What goes here

The contract every PolicyEngine adapter implements PLUS the full
grammar of the reference rule-based engine.

Sections:

1. **The PolicyEngine Protocol** — signature, semantics of allow /
   deny / redact, when to raise PolicyEvaluationError vs return a
   normal deny.
2. **Reference rule grammar** — every field of the YAML rule format
   supported by `harness/policy/rules.py`:
     - match block fields: tool_tags, tool_names, tenants, env,
       any/all/not
     - action: allow | deny | redact
     - reason (deny), redact (redact), id (always)
   With a worked example for each.
3. **Evaluation semantics** — declaration order, first-match-wins,
   default-allow on no match.
4. **Redact action shape** — the redacted-args dict format
   (complete replacement, not a delta).
5. **When to use the reference engine vs OPA/Cedar** — short guide.
   The reference engine handles "deny by tag, redact a field, scope
   by tenant"; OPA/Cedar handle anything with expressions, joins, or
   external lookups.

## What does NOT go here

- The OPA bundle format. Document that under `docs/runbooks/opa.md`
  in `harness-enterprise`.
