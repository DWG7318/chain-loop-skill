# CLK Role Isolation and Verification

## Purpose

Different Codex conversations reduce direct chat-history sharing, but do not alone
isolate workspaces, mutable runtime state, tools, evidence, or anchoring conclusions.
CLK therefore requires procedural and environmental isolation.

## Required isolation layers

| Layer | Worker | Checker | Verification |
|---|---|---|---|
| Conversation/context | Persistent per Chain | Persistent per Chain | Fresh per GO attempt |
| Workspace | Implementation worktree | Clean CELL validation worktree | Clean GO verification worktree |
| Product writes | CELL-scoped | Forbidden | Forbidden |
| Runtime state | Worker namespace | Checker namespace | Verification namespace |
| Evidence | Worker method evidence | Checker CELL evidence | Verification GO evidence |
| Input | Formal CELL | Immutable CELL candidate | Neutral Calabash-grounded GO package |
| Model binding | Versioned per current CELL | Persistent verified binding | Fresh verified binding |
| Lifecycle | Across Chain | Across Chain | One candidate verdict only |

Checker and Verification are especially isolated. They must not share a mutable
workspace, database, browser profile, port namespace, temp directory, generated
success marker, evidence path, or conversation context.

## Pre-binding and activation

At project-plan freeze, every GO receives `GO_VERIFICATION_BINDING`. At Level
activation, before any first CELL dispatch, Supervisor creates the fresh
Verification attempt, binds its clean environment, passes readiness/preflight, and
leaves it uncontaminated until direct Checker intake.

A changed candidate requires a new attempt. Prior Verification context, environment,
or verdict is never reused.

## Immutable candidates

Checker validates an immutable CELL candidate. Verification validates an immutable
GO candidate. Valid identities include exact commit SHA, tree hash, archive hash, or
another collision-resistant artifact identifier.

A mutable directory name, “latest,” or an uncommitted working tree is invalid.

## Environment fingerprint

Every Checker and Verification receipt records:

```text
os_and_arch
tool_versions
dependency_lock_hash
environment_variable_schema_hash
database_or_fixture_namespace
service_ports
browser_profile_id
cache_policy
candidate_identity
```

Secrets are referenced by scope/identifier, never copied into evidence.

## Necessary context versus contamination

Verification must receive enough authoritative context to make a meaningful verdict:

- `PROJECT_CALABASH_BASELINE` hash and relevant content;
- `GO_CALABASH_TRACE`;
- GO and Verification Contract;
- immutable candidate and frozen required outputs;
- environment definition and authorized commands;
- neutral evidence index and safety boundaries.

It must not initially receive:

- Checker recommendation or confidence;
- Worker/Checker transcript;
- hidden reasoning;
- “already passed” claims;
- prior unrelated verdicts;
- mutable Checker state.

Checker provides facts, not a suggested judgment.

## Direct handoff

Checker sends `GO_READY_FOR_VERIFICATION` directly to the pre-established
Verification. Supervisor does not relay or summarize. Verification sends one signed
verdict directly to Checker and Supervisor.

## Same-model use

Checker and Verification may use the same underlying model family only with distinct:

```text
conversation_id
context_id
workspace_id
capability_profile_id
model_binding_id
evidence_path
runtime_namespace
```

Model diversity is an extra defense, not the definition of independence.

Model selection, capability-equivalence proof, reasoning authorization, and model
changes are governed solely by
[`model-selection-and-binding.md`](model-selection-and-binding.md). A change never
mutates the current binding: it creates a new binding and repeats readiness,
isolation, and verification before use.

## Contamination incidents

Record `VERIFICATION_ISOLATION_VIOLATION` when Verification inherits Worker/Checker
context, sees a subjective Checker verdict before deciding, uses mutable Checker
state, edits product artifacts, shares/overwrites evidence, reuses a prior attempt,
or validates a changed candidate/contract.

Invalidate the verdict and launch a fresh attempt from the frozen candidate.
