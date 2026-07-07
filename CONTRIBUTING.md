# Contributing to SHAI

Thank you for taking the time to contribute. SHAI is a security project —
the quality and correctness of every change matters more than speed.

---

## Contributor License Agreement

**All contributions require signing the CLA before your pull request can be merged.**

SHAI is dual-licensed: the core is Apache 2.0 (open source) and SHAI Enterprise
is a commercial product built on top of it. The CLA gives the Maintainer the right
to include your contribution in both, while you retain full rights to use your own
work under Apache 2.0 for any other purpose.

When you open a pull request, the CLA Assistant bot will check whether you have
signed. If not, it will post a comment with instructions. Signing takes less than
a minute: post `I have read the CLA Document and I hereby sign the CLA` as a
comment on your PR. You only sign once.

Read the full agreement: [CLA.md](CLA.md)

---

## Before you start

Read [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/boundaries.md](docs/boundaries.md)
before writing any code. The architecture has deliberate constraints — understand
them before proposing changes. In particular:

- The tool call gate (`check_tool_call`) cannot be disabled and must emit
  exactly one `AuditEvent` per call on every code path. Any change that
  breaks this invariant will not be merged.
- Boundaries never store raw text, arguments, or scanner-matched substrings
  in `AuditEvent` fields. This is a privacy invariant, not a style preference.
- New public API requires discussion before implementation. Open an issue first.

---

## Ways to contribute

**Bug reports** — open a GitHub issue with a minimal reproduction. If the bug
is a security vulnerability, follow [SECURITY.md](SECURITY.md) instead.

**Feature requests** — open a GitHub issue describing the use case before
writing code. Features that expand the public API surface or change gate
semantics need maintainer agreement upfront.

**Documentation** — improvements to `docs/`, `README.md`, or `ARCHITECTURE.md`
are always welcome and do not require an issue first.

**Tests** — additional tests for edge cases, especially around gate bypass
attempts, scanner patterns, and audit invariants, are always useful.

**Bug fixes** — if you have a fix for an open issue, reference the issue in
your PR.

---

## Development setup

```bash
git clone https://github.com/shai-ai/shai
cd shai
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Requires Python 3.11+.

---

## Making a change

1. **Open an issue first** for anything beyond a small bug fix or doc change.
   This saves everyone time — a PR that changes gate semantics without prior
   agreement is likely to be declined regardless of code quality.

2. **Fork and branch** from `main`. Name your branch descriptively:
   `fix/argument-rule-nan-edge-case`, `feat/pattern-rule-case-insensitive`.

3. **Read the files you plan to change** before writing a line. Check what
   imports them. Check the existing tests.

4. **Write tests first** for any behavioral change. The test suite enforces
   several security invariants automatically — your change must not break them.

5. **Run the full test suite** before opening a PR:
   ```bash
   pytest
   ```

6. **One change per PR.** A PR that fixes a bug and adds a feature is two PRs.

---

## Code style

- Follow the existing patterns in the file you are editing
- Pydantic `BaseModel, frozen=True` for all wire types — do not introduce
  mutable dataclasses in the hot path
- No raw text, argument values, or matched substrings in log lines or
  `AuditEvent` fields
- All boundary-facing functions are async
- Scanners implement `async def scan(self, text: str, ctx: AgentContext) -> ScanResult`
- Keep modules focused — one responsibility per file
- Comments explain invariants and contracts, not line-by-line mechanics

---

## Tests

Tests live in `tests/`. The structure mirrors `src/harness/`:

| Directory | Contents |
|---|---|
| `tests/unit/` | Per-module unit tests |
| `tests/contracts/` | Protocol-conformance tests every adapter must pass |
| `tests/integration/` | End-to-end turn tests with real boundaries |
| `tests/security/` | Invariant tests: no raw text in audit, dispatch token integrity |
| `tests/perf/` | Performance baselines for boundary hot paths |

When adding a new scanner or adapter, add a test file in `tests/unit/` and
ensure the relevant contract suite in `tests/contracts/` passes. New adapters
must pass the same contract suite as existing ones — this is the open-core
enforcement mechanism.

Security-invariant tests in `tests/security/` must continue to pass. These
test properties that must hold regardless of configuration, not just default
behavior.

---

## Commit messages

Use conventional commit format:

```
fix(check_tool_call): deny on first argument rule violation before policy

feat(tool): add ArgumentRule pattern constraint with re.search semantics

docs(boundaries): document L2 and L3 gate layers

test(argument_policy): add edge case for nan float comparison
```

Scope to the affected module: `check_tool_call`, `scan_input`, `audit`,
`session_budget`, `argument_policy`, `connectivity`, `config`, `docs`, etc.

---

## Pull request checklist

Before marking your PR ready for review:

- [ ] Tests pass locally (`pytest`)
- [ ] New behavior has test coverage
- [ ] Security invariant tests still pass (`pytest tests/security/`)
- [ ] No raw text, args, or matched content in `AuditEvent` fields
- [ ] Every boundary path still emits exactly one `AuditEvent`
- [ ] Public API changes are reflected in `src/harness/__init__.py`
- [ ] Docs updated if behavior changes (at minimum `docs/boundaries.md`)
- [ ] Commit messages follow conventional commit format

---

## What will not be merged

- Changes that allow `check_tool_call` to be disabled or skipped
- Changes that suppress or conditionally omit `AuditEvent` emission
- Changes that store raw user input, LLM output, or scanner-matched text
  in `AuditEvent` fields
- New public API added to `__init__.py` without a corresponding issue and
  maintainer sign-off
- Changes that weaken an existing security invariant without an explicit
  security justification in the PR description

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating you agree to abide by its terms. Report conduct issues to
**conduct@shai.aibestlabs.com**.

## Contributor License Agreement

All contributions require the CLA. See [CLA.md](CLA.md).
