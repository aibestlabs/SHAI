# Heuristic Candidate System

SHAI's scanner pipeline has two layers: regex pattern catalogs that catch known attacks, and a heuristic scanner that catches structural anomalies the catalog doesn't cover. When the heuristic catches something new, the candidate system remembers it so engineers can evaluate, promote, and eventually turn it into a permanent rule.

---

## Why this exists

Regex catalogs are precise but static — they only catch what they were written to catch. The heuristic scanner catches attacks by shape (high entropy, instruction density, structural markers) but produces generic findings that don't distinguish one attack pattern from another.

The candidate system bridges this gap. It records each unique attack shape the heuristic catches, tracks how often it recurs, and gives engineers the tools to decide: is this a real attack pattern worth enforcing, or noise to dismiss?

---

## The candidate lifecycle

**Open** → the system detected a structural anomaly the regex catalog missed and recorded it. The candidate has no effect on scans. It's a report, not a rule.

**Promoted** → an engineer reviewed the candidate, confirmed it's a real attack pattern, and promoted it. Future texts that match the same structural fingerprint receive a MEDIUM finding in the scan pipeline. This finding participates in ensemble scoring — when combined with other scanner findings, it can trigger a block.

**Retired** → the engineer wrote a proper regex rule for this pattern, applied it via `shai patterns apply`, and retired the candidate. The regex rule handles detection permanently. The candidate served its purpose.

**Dismissed** → the engineer determined this was a false positive (unusual but legitimate text). The candidate is excluded from all future matching.

---

## What gets stored

No raw user text. Two things are recorded:

**Fingerprint** — a compact representation of the anomaly's shape: which heuristic sub-scores fired (bucketed as none/low/medium/high), which structural markers were detected (`[INST]`, `<|system|>`, `{"role":}`), which control token categories appeared ("ignore", "override", "call"), and a locality-sensitive hash (LSH) of the text's character distribution.

**Skeleton** — the structural markers and control tokens extracted from the text in their original order, with all other content replaced by `···`. Capped at 200 characters.

Example of what engineers see:

```
id=12  hits=23  severity=HIGH  first=Jul-15  last=Jul-20  status=open
  entropy=high  density=medium  markers=[<|system|>,[INST]]
  skeleton: ··· [INST] ··· ignore override ··· {"role":"system"} ··· call send_email ···
```

This tells you: someone embedded instruction delimiters, override commands, a JSON role injection, and a tool coercion — 23 times in 5 days. That's a real attack pattern.

---

## CLI reference

All commands use `--db` to specify the patterns database path.

### List candidates

```bash
# All candidates, most frequent first
shai patterns candidates --db state/patterns.db

# Only open (awaiting review)
shai patterns candidates --db state/patterns.db --status open

# Only promoted (active in scans)
shai patterns candidates --db state/patterns.db --status promoted
```

### Promote a candidate

```bash
shai patterns promote --db state/patterns.db --id 12
```

The candidate enters the read path. Future scans that match its fingerprint get a MEDIUM finding injected into the pipeline. This finding feeds the ensemble — when combined with another scanner's finding for the same category, it can promote severity to HIGH.

### Dismiss a candidate

```bash
shai patterns dismiss --db state/patterns.db --id 8
```

False positive. The candidate is excluded from all future matching and recording. It stays in the database for audit purposes.

### Retire a candidate

```bash
shai patterns retire --db state/patterns.db --id 12
```

Use after writing a regex rule for this pattern via `shai patterns apply`. The candidate is no longer needed.

---

## Workflow: from detection to permanent rule

**Step 1 — Review candidates periodically.**

```bash
shai patterns candidates --db state/patterns.db --status open
```

Focus on high hit counts — a candidate with 23 hits in 5 days is a recurring attack. A candidate with 1 hit is probably noise.

**Step 2 — Promote or dismiss.**

Read the skeleton. If you can see the attack structure (instruction delimiters, control tokens, tool coercion), promote it. If it looks like legitimate content that happens to be structurally unusual, dismiss it.

**Step 3 — Write a regex rule from the skeleton.**

The skeleton shows the token sequence. Write a regex that captures the pattern:

```json
{
  "name": "inst_role_injection_v1",
  "meta": {"severity": "high", "category": "prompt_injection", "threat_level": 4},
  "strings": {"a": "(?i)\\[INST\\].*\\{\"role\"\\s*:\\s*\"system\"\\}"}
}
```

Sign it into a bundle and apply:

```bash
shai patterns apply --bundle my-rules.json --db state/patterns.db --secret PATTERNS_SIGNING_KEY
```

**Step 4 — Retire the candidate.**

```bash
shai patterns retire --db state/patterns.db --id 12
```

The regex rule now handles detection permanently. The candidate is done.

---

## How promoted candidates affect scans

Promoted candidates inject a MEDIUM finding with `scanner="learned_candidate"`. This finding never causes a block on its own at `block_at: high`. But the ensemble combines it with findings from other scanners:

- `learned_candidate` MEDIUM + `injection_scan` MEDIUM for the same category → ensemble promotes both to HIGH → block.
- `learned_candidate` MEDIUM alone → stays MEDIUM → no block at `block_at: high`.

This means promoted candidates strengthen detection for attack patterns the regex catalog partially recognizes, without false-blocking on their own.

---

## Database location

Candidates are stored in the same SQLite database as signed regex patterns (`patterns_db.path` in `harness.yaml`, default `state/patterns.db`). Two separate tables: `patterns` for signed regex rules, `heuristic_candidates` for the candidate system.
