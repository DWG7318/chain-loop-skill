---
name: chain-loop-skill
description: Use when the user says CLK or Chain Loop Skill, or uses the legacy names MSLK or multi-small-loop-skill, or when one project needs fixed persistent Chains advancing through ordered fully synchronized Levels with fresh independent GO Verification. Legacy names normalize to CLK. Never trigger together with SLK, GLK, or another loop method.
---

# Chain Loop Skill (CLK)

Use `CLK` as the official abbreviation and `$chain-loop-skill` as the Codex
invocation name. `MSLK` and `$multi-small-loop-skill` are legacy migration terms,
not canonical identities for new runs.
## Canonical Identity

- Product name: `Chain Loop Skill`.
- Abbreviation: `CLK`.
- Canonical repository target: `https://github.com/DWG7318/chain-loop-skill`.
- Legacy repository before rename: `https://github.com/DWG7318/multi-small-loop-skill`.
- GitHub repository ID: `1298120736`.
- Default branch: `main`.
- Version source: repository `VERSION` file and matching `v*` tag.
- Current specification version: `2.6.0`.

Before publishing, verify owner/name, repository ID, default branch, remote HEAD,
tested installation, version file, and release tag. Never publish CLK content to
the SLK repository or another similarly named skill.

## Legacy Name Migration

`Chain Loop Skill (CLK)` replaces the former product identity `Multi Small Loop
Skill (MSLK)`. The execution model remains staged, barrier-synchronized multi-chain
work, but all new contracts, receipts, commands, files, installations, tags, and
runs use `CLK`.

- A user saying `MSLK` or `multi-small-loop-skill` is normalized to CLK for
  explanation and migration.
- Do not create a new formal run with an MSLK identity, receipt prefix, command, or
  folder.
- An active historical MSLK run remains bound to its original version and identity;
  never rewrite its evidence.
- Migration requires a new CLK plan/version, readiness receipts, simulation, role
  bindings, and append-only mapping from old IDs.
- Repository rename and skill-folder rename are release operations; GitHub URL
  redirect does not rename an installed Codex skill automatically.
## Scope

CLK is a staged, barrier-synchronized multi-chain execution method.

```text
Calabash → frozen plan
             ↓
LEVEL-01: GO-01-A  GO-01-B  GO-01-C  GO-01-D
              ↓        ↓        ↓        ↓
            Pair A   Pair B   Pair C   Pair D
              ↓        ↓        ↓        ↓
             Verification per GO candidate
              └──────── full Level barrier ────────┘
                              ↓
LEVEL-02: GO-02-A  GO-02-B  GO-02-C  GO-02-D
```

The number identifies a synchronization Level; the suffix identifies a persistent
Chain. `GO-01-A` is a real GO; `GO-01` alone is not.

All GOs in one Level are launch-ready together and independently verified. The next
Level opens only after every required current-Level GO is `GO_VERIFIED`.

Multiple GOs may be ACTIVE across different Chains in the one open Level, but each
Chain has at most one ACTIVE GO. Concurrency is allowed only with isolated mutable
workspaces or an explicit conflict-safe write plan; safe serialization does not
change the frozen topology.

CLK has fixed Chains, ordered Levels, and full barriers. It has no conditional
branching, partial unlock, cycles, arbitrary runtime routing, or dynamic Chain
creation; those belong to Graph Loop Skill (GLK).

Role types are Supervisor, Checker, Worker, and GO-scoped Verification.
## Mandatory Calabash Definition Gate

Every CLK project requires a frozen `PROJECT_CALABASH_BASELINE`.

Use full Calabash when available. Otherwise Minimum Calabash is mandatory:

```text
Grandpa → Product Architecture → Ontology
```

If none exists, Supervisor derives it from authoritative Owner statements and
project evidence before Worker decomposition, Level/Chain planning, Verification
Contract creation, role launch, simulation, or CELL execution. Supervisor may
normalize uniquely supported definitions but must not invent Owner intent.
Irreducible product-definition ambiguity is `CALABASH_DEFINITION_BLOCKED` and is an
Owner-exclusive matter.

Every GO records a versioned `GO_CALABASH_TRACE` linking its outcome to Grandpa,
the relevant Product Architecture journey/module/outcome, and owned Ontology
concepts/states. Its `GO_VERIFICATION_CONTRACT` must derive from that trace; without
a current source, the GO is invalid.

Read
[`references/calabash-and-chain-loop.md`](references/calabash-and-chain-loop.md)
before planning.
## Twenty-Four Hard Rules

1. Select CLK exactly once for one project run; never combine or switch methods
   inside the active run.
2. Freeze a full or Minimum Calabash before Level/Chain planning or formal role
   launch.
3. Freeze one ordered Level plan and one fixed Chain roster before execution.
4. Use `GO-<LEVEL>-<CHAIN>` identifiers; the numeric part means “same start Level,”
   not a traditional sequential GO number.
5. Every GO in an opened Level must be independently acceptable and launch-ready;
   different Chains may run concurrently, each Chain has at most one ACTIVE GO,
   and the next Level remains closed until the current Level is fully verified.
6. Use one persistent Checker/Worker pair per Chain. Do not add or replace Chains
   during the active run.
7. Keep every role as a visible same-project Codex conversation. A `GO`, `CELL`,
   Round, or plan step is a subtask; only `spawn_agent`, `delegate_task`, hidden,
   or background Agents are subagents, and they are forbidden.
8. Bind every role to separate context, capability, model, evidence, lifecycle,
   and authorized workspace identities; a different title alone is not isolation.
9. Before a GO's first CELL is dispatched, its Verification Contract, direct route,
   model binding, environment template, and fresh attempt instance must be ready.
10. Checker sends a frozen GO candidate directly to its pre-established
    Verification; Supervisor is not a relay.
11. Worker owns product implementation and product rework. Checker and Verification
    never edit product artifacts and accept their own edit.
12. Checker is the sole CELL acceptance and CELL routing authority for its Chain.
13. Verification is the sole GO evidence verdict authority and never plans,
    implements, repairs, routes, or asks Owner.
14. Supervisor owns Calabash, project decomposition, fixed Level/Chain planning,
    deterministic Level barriers, provisioning, Owner-exclusive escalation, and
    final composition audit.
15. All routine work inside the frozen `PROJECT_AUTONOMY_ENVELOPE` proceeds without
    Owner confirmation or per-action authorization.
16. Only an irreducible Owner-exclusive objective, product-definition, credential,
    legal, destructive, irreversible, materially costly, physical, or external
    account matter may reach Owner.
17. Every CELL requires Worker evidence and independent Checker validation against
    the exact immutable CELL candidate.
18. Every GO requires a frozen `GO_VERIFICATION_CONTRACT`, a
    `GO_CALABASH_TRACE`, and fresh independent Verification after all CELLs pass.
19. A CELL in one GO may never wait for or depend on another GO's unfinished CELL,
    mutable intermediate state, or provisional evidence.
20. Cross-GO input is valid only from a `GO_VERIFIED` predecessor and frozen output;
    peer GOs in the same Level cannot depend on one another.
21. Detection is tiered as `CELL_ALWAYS`, `CELL_TRIGGERED`, `GO_BOUNDARY`, and
    `PROJECT_FINAL`.
22. Plans, receipts, evidence, verdicts, and historical decisions are append-only;
    only declared current-state indexes are mutable.
23. Missing roles, unavailable environments, stale evidence, silence, timeout,
    partial artifacts, or green Worker tests never imply acceptance.
24. Completion requires every required GO and Level verified, composition and
    safety gates passed, final evidence present, and `PROJECT_GOAL` satisfied when
    configured.

Schedule, cost, or Owner urgency cannot waive these rules.
## Method Selection Gate

Supervisor selects CLK only when the project can be represented as two or more
fixed Chains progressing through ordered synchronization Levels.

Before freezing the roster, derive the `最大有效 Chain 数量`: after Run/GO
granularity is frozen, choose the highest-cardinality partition that preserves
stable ownership, Chain cohesion, same-Level launch/acceptance independence,
mutable-write isolation, strict local order, full-Run Level barriers, and no
artificial splitting. Resource limits reduce ACTIVE concurrency, not the roster.

For every GO in `LEVEL-01`, prove:

1. **Acceptance independence:** it can be verified without another Level-01 GO's
   unfinished result or evidence, and concurrent writes/state cannot invalidate it.
2. **Level launch independence:** its first CELL can be dispatched in the same Level
   activation cycle without waiting for another GO's future output or decision.
3. **Stable Chain ownership:** one persistent Checker/Worker pair can own the GO's
   write domain and the later GOs on that Chain.

If fewer than two Level-01 GOs satisfy all three conditions, record
`METHOD_SELECTION_FAILED` and do not launch CLK.

A valid CLK plan must also prove that later work can be expressed as ordered Levels
with full barriers. If it needs conditional branches, partial Level unlock, cycles,
arbitrary GO-to-GO routing, dynamic Chain creation, or runtime path choice, record
`METHOD_BOUNDARY_EXCEEDED`; preserve evidence and use a separate GLK run.
## Exclusive Mode Lock

Choose exactly one method before role creation. Once CLK is selected:

- invoke CLK exactly once;
- do not load, nest, repeat, alternate with, or switch to SLK or another loop
  topology;
- do not borrow another method's roles, routing, state, or capabilities;
- preserve accepted evidence if method selection later fails;
- stop new formal work rather than converting the active run.

Shared engineering principles do not make methods composable.
## Visible Conversation Lifecycle

Every role is a visible conversation under the same Codex project.

- Supervisor, Checker, and Worker identities are persistent for the active run.
- Each Chain owns one persistent Checker and one persistent Worker.
- At project-plan freeze, Supervisor records a Verification binding for every
  planned GO.
- At each Level activation, Supervisor creates the fresh Verification attempt for
  every GO in that Level before any first CELL is dispatched.
- Checker sends `GO_READY_FOR_VERIFICATION` directly to that instance.
- Verification sends its signed verdict directly to both Checker and Supervisor.
- Archive a Verification instance immediately after verdict. Any materially changed
  candidate requires a new attempt and new context/environment.
- Archive persistent roles while they have no authorized work; unarchive the same
  role for the next Level rather than creating duplicates.
- No archived conversation performs hidden or background work.
- Each Run has exactly one visible `RUN_PATROL_CONVERSATION` and one heartbeat, normally bound to `gpt-5.6-terra+xhigh` at a frozen 10/15/30-minute interval.
- No method role, including patrol, may Pin a task; only explicit Owner provenance
  is valid, and lifecycle remains independent from Pin state.
## Role and Environment Isolation

Read [`references/role-isolation-and-verification.md`](references/role-isolation-and-verification.md) and
[`references/model-selection-and-binding.md`](references/model-selection-and-binding.md) before role launch.

Every role records:

```text
role_id / role_type / conversation_id / context_id / workspace_id
capability_profile_id / model_binding_id / evidence_path / lifecycle_state
```

Worker implements in its isolated workspace. Checker validates an immutable CELL
candidate in a different clean workspace. Every GO uses a fresh Verification
conversation and workspace created from the immutable GO candidate.

When relevant, Worker, Checker, and Verification must also separate environment
files, database/fixture namespaces, ports, processes, temp paths, browser profiles,
mutable caches, logs, and evidence. Read-only or content-addressed caches may be
shared.

Verification must not inherit Worker/Checker conversations, prior Verification
context, subjective Checker conclusions, hidden reasoning, or mutable Checker state.
`MODEL_BINDING_LEDGER` binds capability equivalence/class, actual model, effort, selection reason/tier, and fresh gates. Technical roles and patrol default to `gpt-5.6-terra+xhigh`.
Only fine-grained, LOW-risk, capacity-PASS Worker CELLs may use `gpt-5.6-luna+xhigh`; only high-complexity correction, root-cause diagnosis, or complex rework may use `gpt-5.6-sol+xhigh`.
GPT 5.5 and lower fail closed; substitutes require content-hashed `PROVEN_EQUIVALENT` evidence, while `ultra` requires item-specific Owner authorization.
Model changes create new bindings and gates; observed drift is forbidden, and same-model roles retain distinct binding, context, workspace, permission, and evidence identities.

If required isolation is unavailable, record `ROLE_ISOLATION_BLOCKED` and fail
closed.
## Mandatory Readiness Eval

Before formal work, Supervisor and every persistent Checker/Worker in the execution
roster must independently pass the CLK readiness Eval with exactly `25/25`:

```text
scripts/run_clk_readiness_eval.py
```

Every fresh Verification instance must also pass `25/25` before receiving a GO
candidate. One wrong, missing, extra, or misordered answer fails the attempt.
Partial credit, manual override, inherited receipts, role substitution, and
answer-key access are forbidden.

Each receipt binds skill/eval hashes, role and scope identity, conversation/context,
model binding, seed, attempt, and per-question result. Any material change makes it
stale.
## Mandatory Simulation Gates

### Project launch simulation

After persistent-roster readiness and Calabash freeze, run a no-side-effect
simulation proving:

1. CLK is the sole selected method.
2. `LEVEL-01` contains at least two acceptance-independent, launch-ready GOs.
3. `GO-01-A` style identifiers map one GO to one Level and one Chain.
4. Every Level-01 GO has a Calabash trace, Verification Contract, pre-bound direct
   route, and isolated Verification environment template.
5. One assignment, delivery, clean Checker validation, and route works per Chain.
6. One Checker directly hands a neutral frozen GO package to Verification without
   Supervisor relay.
7. Verification returns a signed verdict to Checker and Supervisor.
8. The full Level barrier remains closed until all Level members are verified.
9. Routine work proceeds inside the autonomy envelope without Owner authorization.
10. No hidden role, cross-GO CELL dependency, or GLK routing capability is used.

Record `SIMULATION_PASS` or `SIMULATION_FAIL`.

### Level activation gate

Before opening every Level, Supervisor records `LEVEL_START_GATE_PASS` proving:

- every listed GO is ready together;
- every required predecessor Level is `LEVEL_VERIFIED`;
- all frozen upstream GO outputs exist;
- no peer GO dependency exists inside the Level;
- each active Chain has at most one GO in the Level;
- every GO's fresh Verification attempt already passed readiness and preflight;
- all role environments, direct routes, contracts, tools, and autonomy permissions
  are available.

A failed Level gate keeps the whole Level closed.
## Role Authority Matrix

| Responsibility | Sole CLK owner |
|---|---|
| Calabash establishment, normalization, freeze, and version governance | Supervisor |
| Method gate, fixed Chain roster, ordered Level plan, cross-Chain contracts | Supervisor |
| Level start gate, full Level barrier, provisioning, and final composition audit | Supervisor |
| Owner-exclusive assistance and project autonomy envelope | Supervisor |
| Local Chain solution, GO/CELL plan, and evidence-driven local revision | Paired Checker |
| CELL assignment, validation, detection, routing, and local queue | Paired Checker |
| Product implementation and product rework | Worker |
| Independent GO evidence verdict | Fresh Verification attempt for that GO |
| `PROJECT_GOAL` approval | Owner |
| `PROJECT_GOAL` management and final decision | Supervisor using fresh evidence |

No role may silently exercise another role's authority. Supervisor's Level barrier is
a deterministic completeness gate, not Grapher-style path selection.
## Autonomous Completion Rule

CLK completes authorized work without routine Owner authorization.

Before launch, Supervisor freezes a versioned `PROJECT_AUTONOMY_ENVELOPE` derived
from Calabash, the plan, safety rules, tool capabilities, and external-action
boundaries. It pre-authorizes routine work such as scoped file edits, local builds,
tests, scans, non-destructive git operations, temporary test data, approved local
services, and declared verification commands.

Worker, Checker, and Verification must not ask Owner to confirm ordinary
implementation, continuation, code, logs, tests, evidence, recoverable defects,
technically equivalent choices, or actions already inside the autonomy envelope.
No per-CELL, per-GO, or per-Level Owner approval is required.

Uncertainty triggers investigation, independent validation, Worker rework,
Supervisor provisioning, plan repair, or safe recovery—not “please confirm.”

Only Supervisor may contact Owner, and only for one irreducible Owner-exclusive
item: changing Grandpa/product outcome/scope/acceptance/safety, resolving genuine
Calabash ambiguity, supplying inaccessible credentials or legal consent, or
approving destructive, irreversible, materially costly, physical, or external
account action.

A request must contain one item, proof of Owner exclusivity, the consequence of no
action, and the safest choices. Routine escalation is `AUTONOMY_VIOLATION` and
returns to the responsible internal role.

A platform-enforced permission prompt does not automatically create Owner decision
authority. Supervisor must first provision or pre-authorize it. If the platform
cannot proceed without a human action, record `EXECUTION_PERMISSION_BLOCKED` with
exact evidence rather than disguising it as product confirmation.
## Supervisor Contract

Supervisor owns project definition and deterministic multi-chain coordination, not
ordinary CELL traffic.

Supervisor:

- establishes and freezes full or Minimum Calabash;
- derives the project solution, fixed Chain roster, ordered Level plan, and
  cross-Chain contracts;
- freezes `PROJECT_AUTONOMY_ENVELOPE`;
- proves CLK method selection and freezes the persistent roster;
- provisions conversations, model bindings, isolated workspaces, Verification
  templates/attempts, skills, tools, permissions, and versioned device/load facts;
- freezes `DEVICE_CAPACITY_PROFILE`, `CUMULATIVE_ENGINEERING_LOAD`, and Required
  sets; dispatch requires `CELL_CAPACITY_GATE=PASS`;
- freezes every GO's Calabash trace, Verification Contract, and direct route before
  its Level opens;
- records `LEVEL_START_GATE_PASS`, opens all Level members together, and records
  `LEVEL_VERIFIED` only after every required GO verdict is `GO_VERIFIED`;
- maintains the Supervisor board and project-wide progress;
- resolves cross-Chain conflicts, shared prerequisites, safety conditions, plan
  defects, and genuine blockers;
- manages safe pause/resume, patrol alerts, `PROJECT_GOAL`, and final composition
  audit; it ends its turn after control actions and never waits on members with
  `wait_threads`.

Supervisor must not relay normal Checker/Verification messages, plan ordinary CELL
details, execute Worker work, validate a CELL, issue a GO verdict, ask Owner for
routine authorization, add a Chain after launch, partially unlock a later Level, or
perform GLK-style path routing.
## Checker Contract

One persistent Checker controls one persistent Worker on one Chain.

Checker:

- owns its Chain's local solution and the GO/CELL plans assigned by Level;
- writes each GO's Calabash trace, Verification Contract, and tiered detection
  profile inside frozen project boundaries;
- checks Level/GO/CELL continuation conditions;
- packages and sends one CELL at a time, then goes offline;
- validates the immutable CELL candidate in a clean isolated environment;
- records receipts and routes `NEXT`, `CELL_REWORK`, `GO_ACCEPTANCE`, `BLOCKED`, or
  `PLAN_DEFECT`;
- designs Worker-owned rework when product defects are found;
- after all CELLs pass, freezes the complete GO candidate and neutral package;
- sends `GO_READY_FOR_VERIFICATION` directly to the pre-established Verification;
- receives the signed verdict directly, acts on it without changing it, and reports
  local queue/progress.

Checker must not edit Worker-owned product artifacts and self-accept, ask Owner for
routine confirmation, relay through Supervisor when the direct Verification route
is healthy, include persuasive conclusions in the neutral package, declare a GO
verified, change Level membership, or take another Chain's work.
## Worker Contract

One Worker belongs to exactly one Checker and remains the persistent implementation
owner for its domain.

The Worker:

- executes only one formal CELL or rework assignment at a time;
- writes only inside the authorized scope;
- preserves unrelated changes;
- maintains append-only method evidence;
- runs required implementation-side checks;
- returns an immutable candidate identity and evidence;
- reports blockers precisely;
- receives later dependency-ready GOs from the same Checker;
- performs every product correction through a new formal round.

The Worker must not:

- self-select the next CELL;
- broaden scope;
- change acceptance;
- ask the Owner for confirmation or troubleshooting;
- declare its own CELL, GO, stream, or project accepted;
- reuse another Worker's evidence.
## Verification Contract

Every planned GO has a frozen `GO_VERIFICATION_BINDING` before its Level opens. The
binding records role identity, GO/version, contract hash, model binding, fresh
context/environment policy, evidence path, and direct Checker-to-Verification route.

At Level activation, Supervisor instantiates one fresh visible Verification attempt
per GO before any first CELL dispatch. It remains idle and uncontaminated until the
Checker sends the candidate directly.

The neutral package contains:

```text
LEVEL_ID / CHAIN_ID / GO_ID / GO_VERSION
PROJECT_CALABASH_BASELINE_HASH / GO_CALABASH_TRACE_HASH
GO_VERIFICATION_CONTRACT_HASH / PROJECT_PLAN_VERSION
IMMUTABLE_GO_ARTIFACT_ID / FROZEN_REQUIRED_OUTPUTS
AUTHORIZED_VERIFICATION_COMMANDS / ENVIRONMENT_DEFINITION
NEUTRAL_EVIDENCE_INDEX / SAFETY_BOUNDARIES
```

It initially excludes Checker recommendations, confidence, Worker/Checker
transcripts, hidden reasoning, prior verdicts, and mutable state.

Verification independently reproduces the contract in its isolated environment,
executes `GO_BOUNDARY` checks, searches for counter-evidence, and sends one signed
verdict directly to Checker and Supervisor:

```text
GO_VERIFIED
GO_EVIDENCE_GAP
GO_REWORK_REQUIRED
GO_DEFINITION_DEFECT
GO_BLOCKED
```

It never plans, implements, repairs, changes acceptance, chooses the next GO/Level,
routes, or asks Owner. Any material candidate, contract, Calabash, dependency,
environment, tool, or rule change invalidates the verdict and requires a fresh
attempt.
## Worker, GO, and CELL

Use this hierarchy:

```text
Project
  -> ordered LEVEL
      -> one GO per active CHAIN
          -> one or more CELL
              -> ROUND
          -> fresh Verification attempt
```

- **LEVEL:** one synchronization set whose GOs become executable together.
- **CHAIN:** one persistent ownership stream represented by one Checker/Worker pair.
- **GO:** one independently verifiable outcome identified by Level and Chain.
- **CELL:** the smallest inspectable implementation package inside one GO.
- **ROUND:** one immutable attempt, e.g. `GO-01-A/CELL-01-A.01/R02`.
- **Verification:** one fresh independent verdict attempt for one GO candidate.

Canonical identifiers:

```text
LEVEL-01
CHAIN-A
GO-01-A
CELL-01-A.01
```

The numeric GO component denotes the Level. The suffix denotes the Chain. At most
one GO from a Chain may exist in one Level. A Chain may terminate after a verified
GO, but it cannot skip a Level and later reappear. No new Chain appears after
`LEVEL-01`.
## Multi-Chain Level and Barrier Rule

CLK uses a frozen multi-chain Level table, not a free-form runtime graph.

```text
| Level | Chain A | Chain B | Chain C | Chain D |
|---|---|---|---|---|
| 01 | GO-01-A | GO-01-B | GO-01-C | GO-01-D |
| 02 | GO-02-A | GO-02-B | GO-02-C | GO-02-D |
```

When `LEVEL-01` opens, every listed GO can start in the same activation cycle. They
may finish at different times, but `LEVEL-02` remains closed until all Level-01 GOs
have signed `GO_VERIFIED` verdicts. Verified early members freeze their outputs and
wait; only the failed or incomplete Chain continues rework.

Peer GOs in one Level are independent and cannot consume each other's results.
Cross-GO input is allowed only across a completed barrier from a verified predecessor
GO and frozen output.

Forbidden:

```text
GO-01-A/CELL-x -> GO-01-B/CELL-y
GO-01-A/CELL-x -> GO-02-B/CELL-y
GO-01-A verified -> open only part of LEVEL-02
```

Allowed:

```text
all LEVEL-01 GOs GO_VERIFIED
-> LEVEL-01_VERIFIED
-> frozen outputs available
-> LEVEL-02_START_GATE_PASS
-> all LEVEL-02 GOs start together
```

A cross-GO CELL dependency is `GO_BOUNDARY_VIOLATION`. Conditional branching,
partial unlock, cycles, runtime GO routing, or new Chains are
`METHOD_BOUNDARY_EXCEEDED` and require a separate GLK run.
## GO Design

Every GO defines:

- `LEVEL_ID`, `CHAIN_ID`, canonical GO ID, and owner;
- `GO_CALABASH_TRACE`;
- outcome, scope, forbidden scope, and same-Level independence proof;
- prior-Level verified inputs and frozen output references;
- output artifacts/contracts for future Levels;
- `GO_VERIFICATION_CONTRACT` and pre-bound Verification route;
- tiered `GO_DETECTION_PROFILE`;
- CELL map, risk, safety, and autonomy-envelope references;
- candidate/output freeze method;
- completion and failure semantics.

A GO is not the Level itself, a phase label, a conversation, or an arbitrary batch.
## CELL Design

Every CELL defines:

- objective;
- authoritative inputs;
- allowed and forbidden write scope;
- output artifacts;
- dependencies inside the same GO;
- implementation-side checks;
- Checker detection references;
- immutable candidate method;
- Worker model binding;
- evidence and method-log paths;
- completion criteria.

Size CELLs by implementation risk, cross-owner impact, and evidence burden. Reduce
CELL size or concurrency for device safety; never shrink the GO outcome or weaken
acceptance.
## CELL Protocol and Routes

The normal stream is:

```text
Checker -> Worker -> Checker -> Worker -> ...
```

A formal task starts with:

```text
Formal task: GO-01-A/CELL-01-A.01/R01
```

After delivery, the Worker sends:

```text
GO-01-A CELL 1/3 已交付，请检查
```

This is a versioned Required-CELL delivery position, not accepted progress.
`BLOCKED` and `EXECUTION_FAILURE` carry the same GO/CELL/Round and `n/N` identity.

Checker routes:

```text
NEXT
CELL_REWORK
GO_ACCEPTANCE
BLOCKED
PLAN_DEFECT
```

- `NEXT`: CELL accepted; dispatch the next ready CELL in the same GO.
- `CELL_REWORK`: product result failed but the frozen CELL objective remains valid;
  issue a new round to the same Worker.
- `GO_ACCEPTANCE`: all required CELLs accepted; freeze the GO candidate and begin
  fresh Verification.
- `BLOCKED`: an authorized prerequisite or capability is unavailable.
- `PLAN_DEFECT`: objective, architecture ownership, dependencies, scope, or
  acceptance must change.

`REDO` is deprecated. Historical `REDO` records remain valid history but new work
uses `CELL_REWORK` or `PLAN_DEFECT`.
## Product Rework Rule

Product defects return to the Worker through a new formal round.

Checker records:

```text
CELL_REWORK_RECORD
```

with:

- failed candidate identity;
- defect and evidence;
- unchanged frozen objective;
- required outcome;
- permitted scope;
- mandatory regression checks;
- new round ID.

The Checker may repair only Checker-owned validation infrastructure or coordination
metadata. Such a repair must not alter the product candidate and must be fully
recorded before validation restarts in a clean environment.

Verification never repairs anything.
## Topology Fault Localization

Before rework, classify one `TOPOLOGY_FAULT_RECORD` as `CHAIN_LOCAL`, `CROSS_CHAIN_COMPOSITION`, or `LEVEL_BARRIER`. Bind each affected
Chain to one canonical `GO-<LEVEL>-<CHAIN>` candidate and bind `issued_by` to the
explicit class owner/scope: Checker for local, Supervisor for cross-Chain/Barrier.
Keep one valid hypothesis; content-bind scope, evidence, Receipts, controls, exact
partition/closure, and use only a class-valid route. Read
[`references/topology-fault-localization.md`](references/topology-fault-localization.md).
## Detection System

Each Checker maintains a `DETECTION_CAPABILITY_MANIFEST`; every GO owns a
Checker-authored, Supervisor-provisioned `GO_DETECTION_PROFILE`.

Capabilities belong to one tier:

- `CELL_ALWAYS`: Checker runs after every Worker delivery.
- `CELL_TRIGGERED`: Checker runs when a frozen impact predicate is true.
- `GO_BOUNDARY`: fresh Verification runs against the immutable GO candidate.
- `PROJECT_FINAL`: fresh project-final Verification runs when cross-GO technical
  checks are required.

Valid receipts are `RUN_PASS`, `RUN_FAIL`, `NOT_TRIGGERED`, and `BLOCKED`.
`NOT_TRIGGERED` must record the predicate and evidence. Worker checks do not replace
Checker checks; Checker checks do not replace Verification; another domain's
receipt is invalid.

Profile changes require versioned revision and delta simulation. Device limits may
serialize commands, reduce CELL size, or lower concurrency—not acceptance quality.
See
[`references/checker-detection-catalog.md`](references/checker-detection-catalog.md).
## Run Verification Layers

Read
[`references/run-lifecycle-and-verification.md`](references/run-lifecycle-and-verification.md)
and
[`references/receipt-and-state-contracts.md`](references/receipt-and-state-contracts.md)
before formal Run execution.

CLK uses `D0 -> D1 -> D2 -> conditional LEVEL -> D3`:

- D0 is Worker implementation evidence, never acceptance.
- D1 is Checker acceptance of one immutable CELL candidate.
- D2 is fresh Verification of one GO composition.
- LEVEL is fresh Verification only for a new cross-Chain claim not proved by D2.
- D3 is fresh Verification of the final frozen Run Feature.

Higher layers consume signed lower Receipts and never blindly repeat them. D2,
LEVEL, and D3 each require a distinct fresh attempt, context, visible conversation,
clean workspace, evidence directory, and candidate binding. A Required GO still in
the Baseline requires D2 PASS. An Optional GO must reach D2 PASS or a declared
non-active terminal state before the full Level barrier can pass.
## GO Evidence Acceptance

Every GO freezes its Calabash trace and `GO_VERIFICATION_CONTRACT` before Level
activation. The Contract defines the claim, observable outcomes, evidence,
reproducibility, counter-evidence, pass/fail rules, GO-boundary checks, downstream
outputs, safety, version, and hash.

Before the GO's first CELL, its fresh Verification attempt is already provisioned,
ready, isolated, and directly addressable by Checker.

After all required CELLs pass:

1. Checker freezes the GO candidate and neutral package.
2. Checker sends `GO_READY_FOR_VERIFICATION` directly to Verification.
3. Verification independently validates and sends a signed verdict directly to
   Checker and Supervisor.
4. Supervisor updates only project/Level state; it does not relay or rewrite the
   verdict.

Handling:

- `GO_VERIFIED`: Checker closes GO and freezes outputs; Supervisor marks that Level
  member verified.
- `GO_EVIDENCE_GAP`: Checker adds bounded evidence work inside the same GO or records
  a plan defect.
- `GO_REWORK_REQUIRED`: Checker issues Worker-owned rework.
- `GO_DEFINITION_DEFECT`: Checker proposes a versioned GO/Contract revision;
  Supervisor governs Calabash, Level, cross-Chain, safety, and Owner boundaries.
- `GO_BLOCKED`: Supervisor resolves the condition within authority.

A changed candidate requires a new fresh Verification attempt. Only `GO_VERIFIED`
completes a GO; only all required verified members complete a Level.
## Evidence-Driven GO Revision

After every GO verdict, Checker compares plan and actual result: scope, defects,
residual risk, dependencies, estimates, and incomplete outcomes.

Before `GO_VERIFIED`, Checker may revise CELLs, evidence work, detection allocation,
or model assignment inside the same frozen GO outcome. A changed outcome, Calabash
trace, scope, acceptance, or ownership is `PLAN_DEFECT`.

For unstarted future work, Checker may propose changed GO detail in its own Chain.
Supervisor may approve only when the versioned amendment preserves:

- the fixed Chain roster;
- ordered Levels and full barriers;
- one GO per active Chain per Level;
- no same-Level dependency;
- no cross-GO CELL dependency;
- Calabash traceability and autonomy/safety boundaries.

Missing historical work may be placed in an append-only supplementary future Level
when it remains a deterministic barrier plan. Conditional routing, partial unlock,
new Chains, cycles, or arbitrary insertion is `METHOD_BOUNDARY_EXCEEDED`.

Never rewrite historical GO, CELL, evidence, or verdict. Record old/new plan,
trigger evidence, impact, and `GO_REVISION_SIMULATION_PASS` before dispatch. A
changed candidate always requires a new fresh Verification attempt.
## Continuation Condition Gate

Before every Worker assignment, Checker verifies:

- current `LEVEL_START_GATE_PASS` and active Level membership;
- authoritative inputs and same-GO CELL dependencies;
- every required prior Level is `LEVEL_VERIFIED`;
- upstream GO outputs are verified and frozen;
- no peer GO in the same Level is an input;
- allowed scope, tools, credentials, safety, and acceptance;
- the action is inside `PROJECT_AUTONOMY_ENVELOPE` or has an authorized internal
  resolution.

If a condition clearly fails, stop dispatch and record `CONDITION_BLOCKED` with
evidence. Checker never sends filler, speculative, or waiting work.

Supervisor resolves the condition under existing authority and records
`RESUME_AUTHORIZED`, or emits one precise `OWNER_ASSISTANCE_REQUIRED` only for a
proven Owner-exclusive item. Checker revalidates before resume.

Other independent GOs in the active Level may continue when the block cannot
invalidate them, but the next Level remains closed until the full barrier passes.
## Dispatch, Wake, and Patrol

Before dispatch, Checker completes gates, snapshots, and capability preflight; each active dispatch binds one pair/scope and exactly one complete wake lifecycle.
Worker alone may wake its frozen Checker: direct message at T+0; at T+2 read/list/unarchive and re-resolve the same Checker without guessing/replacement;
at T+4 create/update one deterministic heartbeat; at T+6 write `PENDING_WAKE`.
Each level waits at most two injected-clock minutes.

Checker first emits scoped `WAKE_ACK`; matching ACK or processing proof stops escalation, deletes heartbeat, and consumes `PENDING_WAKE`. Supervisor never loops
or waits with `wait_threads`; zero-time snapshots are allowed. The sole patrol
consumes pending wakes and reports only mechanical Run faults using a complete fixed check set, status/finding enums, and bound observation/evidence. `LOW→10`,
`MEDIUM→15`, `HIGH→30` follows project workload. It never checks
quality, repairs, takes over, dispatches, Pins, or creates roles. At
`LOOP_TERMINAL`, it deletes heartbeat, records `PATROL_CLOSED`, and archives itself.
The full machine rules are in
[`references/worker-wake-patrol-and-progress.md`](references/worker-wake-patrol-and-progress.md).
## Pre-Authorized Worker Execution Gate

Before dispatch, Supervisor provisions the pair under the frozen autonomy
envelope; Checker binds the canonical Worker workspace, confirms the CELL allowlist,
and records `WORKER_EXECUTION_GATE_PASS`. Routine execution requires no Owner
authorization.

Unexpected credentials, external side effects, destructive/security-sensitive
actions, out-of-scope writes, and objective/acceptance changes route internally to
Supervisor and only then to Owner when genuinely Owner-exclusive.
## Progress and CELL Capacity

Checker is the finest progress authority: each unique D1 decision has exactly one bound progress update, and only one effective D1 PASS adds to
`D1_ACCEPTED`; delivery, tests, checking, rework, blocks, and duplicates do not. It
reports `a/N`, unchanged on failure, and sends Supervisor one
`GO_CANDIDATE_READY` milestone only after all Required CELLs are accepted. That
state is not `D2_VERIFIED`.

Supervisor reports exactly once per substantive GO/Level/Run trigger, counting current D2 verdicts and verified Levels. Verification emits verdicts only; patrol emits no
engineering progress. Denominators come from versioned Required sets; amendment or
split shows the new version/recomputed denominator without rewriting history. Keep
`DELIVERED`, `D1_ACCEPTED`, `GO_CANDIDATE_READY`,
`D2_VERIFIED`, `RUN_VERIFIED`, and `OWNER_ACCEPTED` distinct.

CELL size is total engineering cost: implementation, dependencies, build/test/
recheck/regression, evidence/hash/cleanup, context, services, retry, and cumulative
coupling. Unknown capacity fails closed. Only `CELL_CAPACITY_GATE=PASS` dispatches;
other results are `SPLIT_REQUIRED` or `CAPACITY_BLOCKED`. Pre-dispatch split keeps
GO outcome/acceptance and creates no subagent. Worker never splits; excess becomes
`CELL_SCOPE_EXCEEDED` with evidence. A post-dispatch 3+ split is
`CELL_OVERSIZE_SEVERE` and re-evaluates remaining plan/device facts. Refresh load at
GO/Level/Graph boundaries or measured deviation; logical parallelism never implies
unbounded device command concurrency.
## Run Owner Acceptance and LCCoding Boundary

After fresh D3 PASS, Supervisor immediately facilitates one bounded Run-product
Owner Acceptance. Allowed verdicts are `LOOP_OWNER_ACCEPTED`,
`LOOP_PRODUCT_REWORK`, `PRODUCT_DEFINITION_CHANGE`, and `NEW_FEATURE_REQUEST`.

`LOOP_OWNER_ACCEPTED` means `RUN_PRODUCT_ONLY`; it must record
`project_security_closed: false` and `delivery_authorized: false`. CLK returns the
candidate and evidence to LCCoding. Centralized project vulnerability audit,
Post-Security Owner Acceptance, and Delivery remain outside CLK. Read
[`references/lccoding-interface.md`](references/lccoding-interface.md).
## Optional Project Goal Gate

Use `PROJECT_GOAL`, never the ambiguous bare term `Goal`.

The Owner may explicitly define one versioned `PROJECT_GOAL` with:

- identifier;
- objective;
- measurable success criteria;
- required project-wide evidence;
- safety boundaries.

Supervisor must not invent, broaden, or silently change it.

Checker stream completion remains provisional until all required GOs are verified.
Supervisor independently evaluates the `PROJECT_GOAL` against fresh project-wide
evidence and project-final Verification verdicts when configured.

Record:

```text
PROJECT_GOAL_SATISFIED
```

only when every criterion is proved.

Otherwise record:

```text
PROJECT_GOAL_GAP
```

with unmet criteria, evidence, residual risk, affected domains, and required
outcome. Affected Checkers author append-only continuations for their persistent
Workers. Supervisor does not author ordinary local plans.
## Mutable State and Append-Only Evidence

Append-only artifacts include:

- accepted and superseded plans;
- GO/CELL files and revisions;
- Worker method logs;
- Checker receipts;
- Verification packages, evidence, and verdicts;
- queues;
- control receipts;
- incident and recovery records.

Explicitly mutable current-state artifacts are limited to:

```text
WORK_CONTINUATION_INDEX
Supervisor board current-status section
ephemeral progress cache
```

Mutable indexes point to history; they do not replace it.
## Markdown Context Boundary

Every governed Markdown file has a hard maximum of 1000 physical lines. The
`WORK_CONTINUATION_INDEX` remains below 200 physical lines.

Split at semantic boundaries such as Worker domain, GO, coherent CELL group,
verification package, evidence batch, or completed decision. Never hard-cut a
requirement, table, code block, acceptance record, or evidence chain.

Every GO that can write Markdown assigns `markdown-line-budget` in its detection
profile. Every accepted CELL records line-count evidence. Before the next append
would exceed the limit, seal the current shard and continue in a linked successor.
## Evidence and Queue Paths

Use project-local paths unless stricter ones exist:

```text
coordination/
  plans/ checker-messages/ worker-method-logs/
  checker-evidence/ verification-packages/ verification-evidence/
  queues/ supervisor-board.md work-continuation-index.md
```

Worker, Checker, and Verification evidence remain separate. A verdict binds GO and
contract versions, immutable artifact, Verification role/conversation/context/
workspace/model binding, environment fingerprint, evidence hash, and verdict.

Only Checker writes its Worker stream queue. A stream is passed only after every
assigned GO is `GO_VERIFIED` and Supervisor final audit accepts it.
## Recovery Rules

- **Delayed conversation registration:** confirm the returned ID before creating a
  replacement.
- **Duplicate Checker or Worker:** choose one authoritative pair, stop/archive the
  duplicate, and execute each CELL once.
- **Duplicate Verification:** invalidate both if either saw the other's conclusion;
  launch one fresh clean Verification.
- **Lost Verification context:** discard the incomplete verdict and launch a fresh
  Verification from the same immutable candidate.
- **Contaminated Verification input:** record
  `VERIFICATION_ISOLATION_VIOLATION`; no verdict is valid.
- **Worker system error:** Checker inspects usable immutable output; if none exists,
  re-dispatch the original CELL as a new round.
- **Damaged method log:** seal it, preserve the incident, create a linked shard, and
  revalidate current artifacts.
- **Repeated product defect:** issue bounded Worker rework; escalate only a real
  plan defect or blocker.
- **Dynamic external data:** distinguish legitimate drift from current-CELL writes
  through semantic and writer-attribution evidence.
- **Unavailable role or environment:** fail closed; never substitute another role.

Never auto-advance from silence or timeout.
## Final Project Composition Audit

Supervisor closes the project only after:

- every required Worker stream has a passed queue;
- every required GO has a current `GO_VERIFIED` verdict;
- every verdict binds the final artifact and contract identities;
- cross-Worker contracts and frozen outputs compose correctly;
- required `PROJECT_FINAL` checks pass;
- hard brakes and safety conditions are clear;
- no unresolved blocker, plan defect, evidence gap, or isolation violation exists;
- the optional `PROJECT_GOAL` is satisfied;
- the final candidate handoff, evidence index, and queue record exist.

Supervisor final audit is not a second CELL check and not a substitute for
Verification.
## Launch Checklist

Before project launch, Supervisor confirms:

- frozen full/Minimum Calabash and no unresolved definition block;
- sole-method selection and a fixed roster of at least two Chains;
- ordered Level table using `GO-<LEVEL>-<CHAIN>` identifiers;
- every Level-01 GO is independent and launch-ready;
- no conditional branch, partial unlock, cycle, dynamic Chain, or GLK capability;
- current `25/25` readiness and project `SIMULATION_PASS`;
- visible persistent roles with isolated identities/environments;
- exactly one Luna+xhigh Run patrol/heartbeat and no method-role Pin capability;
- `PROJECT_AUTONOMY_ENVELOPE` covers routine work without Owner authorization;
- versioned device/load facts and PASS capacity gates for dispatchable CELLs;
- every GO has Calabash trace, Verification Contract/binding, CELL plan, and tiered
  detection profile;
- cross-GO inputs exist only at verified Level boundaries;
- append-only/mutable boundaries, Markdown limits, recovery, and final audit exist.

Before each Level opens, require `LEVEL_START_GATE_PASS`, fresh Verification
attempts and direct routes for every GO, all prior Levels verified, all inputs
frozen, and all first CELLs ready together.

Before each GO verdict, require all CELLs accepted, immutable candidate/contract,
fresh isolated Verification, neutral direct package, and no downstream Level work
from provisional output.
## Migration

Active 1.8.3 MSLK and pre-2.6.0 CLK runs remain bound to their historical
specifications. Preserve old receipts and read the matching migration guide:
[`../MIGRATION-MSLK-TO-CLK.md`](../MIGRATION-MSLK-TO-CLK.md),
[`../MIGRATION-2.0-TO-2.3.1.md`](../MIGRATION-2.0-TO-2.3.1.md), or
[`../MIGRATION-2.3.1-TO-2.4.0.md`](../MIGRATION-2.3.1-TO-2.4.0.md). For 2.4.0,
read [`../MIGRATION-2.4.0-TO-2.5.0.md`](../MIGRATION-2.4.0-TO-2.5.0.md); for 2.5.0,
read [`../MIGRATION-2.5.0-TO-2.6.0.md`](../MIGRATION-2.5.0-TO-2.6.0.md).
If unfinished work cannot retain fixed Chains, ordered Levels, and full barriers,
record `METHOD_BOUNDARY_EXCEEDED` and use a separate GLK run.
## Version Note

CLK 2.6.0 preserves 2.5.0 topology/runtime semantics while adding evidence-bound,
controllable model selection and verified switching. Dynamic graphs stay GLK-only.
