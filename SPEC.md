# Chain Loop Skill Standard Specification 2.5.0

## 1. Identity and boundary

The canonical product name is `Chain Loop Skill`, abbreviated `CLK`. `Level` is
the synchronization unit. `Chain Loop Kit` may describe repository packaging but
is not a product rename. `Stage` is not a canonical CLK topology term.

CLK governs one bounded engineering Run whose work is honestly representable as
at least two fixed, ordered Chains coordinated by full Level barriers. LCCoding
owns surrounding product formation, centralized project security closure, and
Delivery.

## 2. Required input

CLK requires a frozen `RUN_CONTRACT` containing the Run and Feature Slice IDs,
Calabash baseline reference and hash, Run Feature, scope and forbidden scope,
acceptance claims, evidence requirements, autonomy envelope, safety boundary, and
immutable candidate-binding policy. Material gaps are `RUN_CONTRACT_INCOMPLETE`.

Full or Minimum Calabash remains mandatory. Every GO binds a current
`GO_CALABASH_TRACE` and a Verification Contract derived from it.

## 3. Method selection

Use CLK only when all are true:

1. at least two meaningful stable Chains exist;
2. every Chain has strict local GO order;
3. all work fits ordered, full-barrier Levels;
4. one Chain contributes at most one GO per Level;
5. same-Level GOs are acceptance-independent and launch-ready together;
6. no free branch, partial unlock, cycle, dynamic Chain, or arbitrary GO edge is
   required.

The Chain roster uses the `最大有效 Chain 数量`. Freeze the Run and GO granularity
first, then choose the highest-cardinality valid partition that preserves stable
ownership, Chain cohesion, Level-01 launch independence, same-Level acceptance
independence, mutable-write isolation, strict local order, and valid full-Run Level
barriers without artificial splitting. Resource limits may reduce ACTIVE
concurrency, but they do not shrink or merge the frozen roster.

Use SLK for one strict line and GLK for a free execution graph.

## 4. Canonical objects

- `Run`: one frozen bounded engineering outcome.
- `Chain`: one persistent ordered implementation stream.
- `Level`: one synchronization set whose GOs become executable together.
- `GO`: one independently verifiable engineering outcome in exactly one Chain and
  one Level.
- `CELL`: the smallest controlled implementation package inside one GO.
- `Attempt`: one immutable execution or verification try.
- `Receipt`: one signed evidence verdict bound to immutable identities.
- `Barrier`: the complete transition proof from one Level to the next.

Canonical IDs use `LEVEL-01`, `CHAIN-A`, `GO-01-A`, and `CELL-01-A.01`.

## 5. Topology and concurrency invariants

1. The Chain roster and Level plan freeze before execution.
2. Every GO belongs to exactly one Chain and one Level.
3. GO order along a Chain follows its frozen `go_order` exactly.
4. Level ordinals are unique positive integers and strictly increase.
5. A Chain contributes at most one GO to one Level.
6. Only one Level is open.
7. A GO outside the open Level cannot be ACTIVE.
8. Each Chain has at most one ACTIVE GO.
9. Multiple different Chains may have ACTIVE GOs in the open Level.
10. Every Level member is launch-ready in the same activation cycle.
11. No same-Level peer dependency or cross-GO CELL dependency is allowed.
12. The next Level cannot open until the full current-Level Barrier passes.

Concurrency is allowed, not mandatory. Device, workspace, write-set, rollback, or
risk constraints may serialize eligible GOs without changing topology.

## 6. Roles and authority

- Supervisor owns Calabash governance, method selection, the frozen Chain/Level
  plan, autonomy, provisioning, Level gates, amendments, Owner-exclusive
  escalation, and final composition control. It signs no D1, D2, LEVEL, or D3
  product verdict.
- One persistent Checker/Worker pair owns each Chain.
- Worker alone edits product artifacts and emits D0.
- Checker independently validates immutable CELL candidates and emits D1.
- Fresh Verification attempts emit D2, conditional LEVEL, and D3 verdicts.
- Owner performs bounded Run-product acceptance after D3 PASS.

No role may accept its own product edit or silently exercise another role's sole
authority.

## 7. Evidence layers

### D0 — Worker

D0 proves implementation-side behavior for one immutable CELL candidate. It is
evidence, not acceptance.

### D1 — Checker

D1 independently proves the immutable CELL candidate satisfies its frozen CELL
Contract. A failed product result returns to Worker through a new round.

### D2 — GO Verification

D2 is a fresh isolated Verification attempt proving accepted CELLs compose the
frozen GO claim. It consumes D1 receipts and searches for counter-evidence.

### LEVEL — conditional composition Verification

LEVEL Verification is required only when a new cross-Chain technical claim exists,
including cross-Chain data dependency, shared mutable state, a combined Level
claim, shared external-resource risk, or inability of D2 receipts alone to prove
the Barrier claim. The decision and reason are auditable.

### D3 — Run Verification

D3 is a fresh isolated attempt proving verified GOs and Levels compose the frozen
Run Feature on the final candidate.

Higher layers consume signed lower receipts. Blind repetition is forbidden.
Repetition requires a changed candidate or environment, stale or conflicting
evidence, a composition effect, expanded regression scope, or a specific new risk.

## 8. Verification isolation

Every D2, LEVEL, and D3 verdict uses a distinct attempt ID, fresh context and
visible conversation identity, clean workspace, evidence directory, environment
fingerprint, and immutable candidate binding. One independent Verification identity
may perform several layers only through these separate attempts.

Prior formal receipts may be consumed. Prior hidden reasoning, mutable state, or
subjective conclusions may not be inherited. Candidate or Contract changes
invalidate the attempt and require a new one.

## 9. Topology fault localization

Before changing a product candidate in response to a failure, CLK records one
append-only `TOPOLOGY_FAULT_RECORD` bound to the Run, Baseline, Level, affected
Chains, candidate digests, attempts, and Receipt/evidence hashes. `fault_class` is
exactly one of `CHAIN_LOCAL`, `CROSS_CHAIN_COMPOSITION`, or `LEVEL_BARRIER`.

Every affected Chain binds exactly one immutable Candidate, and its GO ID equals
the canonical `GO-<LEVEL>-<CHAIN>` derived from the record's Level and Chain.
`issued_by` binds to an explicit actor/responsibility/scope tuple rather than an
identity-name guess: `CHAIN_LOCAL` belongs to its paired Checker and affected
Chain; cross-Chain composition and Level Barrier records belong to Supervisor at
the Level. No Debugger role exists.

One fault series has at most one active hypothesis. Each record contains one
statement, predicted observation, falsifier, and evidence set. A falsified record
is sealed; a new record links it through reciprocal supersession. Guessing does not
authorize a product change.

The Receipt catalog is nonempty and partitions exactly into invalidated and
preserved sets. Hypothesis evidence is a subset of the record's content-hashed
evidence, and each source attempt is bound to the actual D0/D1 CELL, D2 GO,
LEVEL/BARRIER Level, or D3 Run scope. Record state and hypothesis status use only
the declared legal pairs; sealed records require valid reciprocal successor links.

A healthy same-Level Chain is a differential control only when a frozen interface,
input, or environment basis proves comparability. Its D2 Receipt remains its own:
its preserved catalog ID, hash, D2 layer, and same-Level GO scope must match, and it
cannot accept the failed Chain or create a same-Level dependency.

Changed Receipt identities propagate only along declared consumption edges. The
resulting transitive set is the exact invalidation and reverification closure;
unrelated Receipt identities remain valid. With unchanged D2 candidates, a
cross-Chain composition probe is LEVEL-only. A pure `LEVEL_BARRIER` correction
preserves all technical Receipts and recalculates only the Barrier.

Native routes are class-bound: `CHAIN_LOCAL` uses `CELL_REWORK` or
`GO_REWORK_REQUIRED`, `CROSS_CHAIN_COMPOSITION` uses `LEVEL_REVERIFICATION`, and
`LEVEL_BARRIER` uses `BARRIER_RECALCULATION`.

Local patching stops when evidence requires a changed outcome, scope, acceptance,
ownership, dependency, Chain/Level plan, or topology. Route such evidence as
`PLAN_DEFECT`; route a product-definition contradiction as
`CALABASH_REVIEW_REQUIRED`; route partial unlock, cycles, dynamic Chains, or
runtime path choice as `METHOD_BOUNDARY_EXCEEDED`. These are handoff boundaries,
not new CLK roles or verification layers.

## 10. Worker wake, Supervisor wait, and Run patrol

Only Worker may use the four-level wake ladder, and only toward its originally
bound Checker after a formal CELL delivery, BLOCKED result, or execution failure.
Dispatch freezes Checker thread/host and Run/GO/CELL/Round scope and preflights
send/read/list/unarchive, temporary-heartbeat, and PENDING_WAKE capabilities.
Every active `CELL_DISPATCH` must bind one current Worker/Checker and exactly one
same-scope wake lifecycle. An `INITIAL_UNDISPATCHED` trace may have no wake; an
active trace, orphan Worker signal, or erased event ledger cannot use that exception.

Worker sends one scoped GO/CELL `n/N` signal at T+0, inspects and may unarchive or
re-resolve the same Checker at T+2, upserts one deterministic temporary heartbeat
at T+4, and writes PENDING_WAKE at T+6. Each injected-clock window is at most two
minutes. Matching `WAKE_ACK` or mechanical processing evidence stops later levels.
No identity guessing, replacement Checker, duplicate work, real test sleep, or
general role message bus is allowed.

Supervisor cannot wait through `wait_threads`, loop it, or wait for all Workers.
Zero-time snapshots remain allowed; Supervisor ends its turn after dispatch or
control.

Each Run has exactly one visible `RUN_PATROL_CONVERSATION`, one heartbeat, model
`gpt-5.6-luna`, reasoning `xhigh`, and frozen 10/15/30-minute interval. Patrol is
non-authoritative, performs no product work, acceptance, repair, redispatch, or
engineering-progress reporting, and does not alter CLK role/D-layer enums. It
mechanically reports unexplained stalls, PENDING_WAKE, forbidden Agent evidence,
Supervisor wait, duplicate patrol, Pin provenance errors, and missing terminal
closure. Formal pause, legitimate block, and documented external wait are normal.
Project workload maps `LOW→10`, `MEDIUM→15`, and `HIGH→30` minutes. Every patrol
status carries the complete fixed check set plus evidence; every alert uses a fixed
finding and binds its observation/evidence identity. Free-form “normal” is invalid.

GO, CELL, Round, plan step, and the Chinese term `子任务` are subtasks. A visible
same-project task with stable thread ID is a peer conversation, not a subagent.
Only spawn/delegate/hidden/background Agent capabilities constitute subagents.

## 11. Layered real-time progress

Worker delivery signal contains GO ID, CELL ordinal, current Required CELL total,
and delivered/check, BLOCKED, or execution-failure semantics. It never increments
accepted progress and all wake levels retain one progress identity.

Checker ACKs first and derives `accepted_cell_count` only from unique current
effective D1 PASS Receipts. FAIL, rework, BLOCKED, duplicate Receipt, green Worker
tests, and inspection do not increment. Checker sends Supervisor no CELL stream;
only a GO boundary yields `GO_CANDIDATE_READY`, `VERIFYING`, or `D2_VERIFIED`, and
candidate ready never substitutes for D2.
Each unique D1 decision/Receipt has exactly one same-scope Checker progress update.
Each material GO/Level/Required-set/Run/D3/Owner trigger has exactly one later
Supervisor update; omission, duplication, reordering, or trigger reuse is invalid.

Supervisor emits only substantive GO/Level/frozen-graph-or-manifest/Run/D3/Owner
updates. Its current-Level GO numerator is current D2 `GO_VERIFIED`; its Level
numerator is verified Levels. Denominators come from the current versioned Required
set. Amendment activates a new version, explicitly preserves evidence, and
recomputes counts without rewriting history. Controlled states are `DELIVERED`,
`D1_ACCEPTED`, `GO_CANDIDATE_READY`, `D2_VERIFIED`, `RUN_VERIFIED`, and
`OWNER_ACCEPTED`. Verification emits verdicts only; patrol emits no engineering
progress.

## 12. CELL capacity planning

Before Run/plan freeze, Supervisor freezes a versioned, measured or conservative
`DEVICE_CAPACITY_PROFILE` for CPU, available RAM, applicable GPU/VRAM, disk/IO,
network/external services, processes/ports, safe command concurrency, command/test/
build duration, context, and evidence budgets. Relevant unknown capability is
`CAPACITY_BLOCKED`; vague resource prose is invalid.

Versioned `CUMULATIVE_ENGINEERING_LOAD` records code/dependency/artifact size,
regression time, peak memory, evidence/hash volume, context reload, external cost,
and accepted-baseline coupling at Run/GO/Level/frozen graph-manifest/feedback
boundaries. Every unstarted CELL is re-estimated after material feedback.

Each CELL binds total engineering cost, including implementation, dependencies,
artifacts, test matrix, Checker verification, regression, evidence/hash/cleanup,
context, tools/services, rollback/retry, and cumulative coupling. The mechanical
gate is exactly `PASS`, `SPLIT_REQUIRED`, or `CAPACITY_BLOCKED`; only current PASS
permits dispatch.

Pre-dispatch split preserves GO outcome/acceptance and verification quality and
produces independently deliverable, independently D1-checkable CELLs without new
GO, Worker, or agent. Worker cannot split; actual overrun emits
`CELL_SCOPE_EXCEEDED` with immutable checkpoint/evidence. Post-dispatch split emits
`POST_DISPATCH_CELL_SPLIT`; three or more successors also emit
`CELL_OVERSIZE_SEVERE` and force remaining-plan/device/load reassessment. Six,
seven, and eight successors are always severe. Split versions the fifth-rule
Required denominator and does not increment acceptance. Logical Level concurrency
may safely use lower serialized device-command concurrency without inventing GO
dependencies.

## 13. Thread Pin prohibition

The canonical technical-role matrix remains exactly Supervisor, Checker, Worker,
and Verification. Patrol stays a separate non-authoritative binding. Both that
matrix and the patrol binding deny `set_thread_pinned(true)`. Creation,
dispatch, ACTIVE, wait, BLOCKED, rework, verification, milestone, persistence, and
importance never imply authorization. Pin cannot replace registry, status,
progress, recovery, archive, or unarchive.

Only Owner UI choice or current-Run item-specific Owner authorization is legal.
Agent/method Pin records `UNAUTHORIZED_THREAD_PIN`, even after later unpin. Unknown
provenance records `PIN_PROVENANCE_UNKNOWN`; patrol reports but cannot unpin or
guess provenance.

## 14. Level Barrier

Barrier PASS requires:

- every still-Required GO has D2 PASS bound by Receipt ID and hash;
- every Optional GO is D2 PASS or in `CANCELLED`,
  `DEFERRED_BY_AMENDMENT`, or `SUPERSEDED`;
- no Optional GO is ACTIVE, pending, or unresolved;
- the conditional LEVEL Verification decision is recorded;
- the LEVEL Receipt is PASS when required;
- the candidate set and evidence are synchronized;
- no blocker invalidates the claim;
- no unresolved topology fault references the current Level;
- one atomic transition closes the current Level before the next opens.

`formal resolution` never substitutes for D2 PASS while a GO remains Required in
the Baseline. Governance may use an approved amendment to cancel, remove, defer, or
supersede the GO; only the amended Baseline participates in Barrier calculation.

## 15. Runtime state

The mutable runtime index records the current Run, open Level, per-Chain current and
ACTIVE GO, GO/Level state, verification attempts, workspace/write scopes, latest
Barrier evaluation, open topology-fault references, snapshot ID, and last
append-only event ID. It is a pointer to history, not a replacement for immutable
Receipts, topology-fault records, or amendments.

Level close, Barrier PASS, and next-Level open are recorded as an atomic transition.

## 16. Receipt envelope

Every technical Receipt binds receipt type and ID, Run/Feature Slice, Baseline and
Contract versions/hashes, attempt, immutable candidate digest, actor and sole
responsibility, verification context reference, environment/workspace, evidence
path/hash, issue time, consumed Receipts, invalidation/supersession, result, and
failure reason.

Verification context detail is stored once in a frozen referenced artifact rather
than duplicated in every Receipt.

## 17. Amendments

Frozen structure changes only through `CHAIN_AMENDMENT`, `LEVEL_AMENDMENT`, or
`GO_AMENDMENT`. Every amendment binds identity, version, state, authority, time,
reason and evidence, before/after Baseline hashes, structural before/after values,
affected attempts and Receipts, invalidation and reverification requirements, and
supersession links. Historical records are never rewritten.

Product-definition changes return to LCCoding/Calabash governance.

## 18. Owner Acceptance and security boundary

After D3 PASS, Supervisor immediately presents the current bounded Run candidate,
entry point, concise steps, visible outcomes, limitations, and D3-covered invisible
risks. Allowed Owner verdicts are:

```text
LOOP_OWNER_ACCEPTED
LOOP_PRODUCT_REWORK
PRODUCT_DEFINITION_CHANGE
NEW_FEATURE_REQUEST
```

`LOOP_OWNER_ACCEPTED` has scope `RUN_PRODUCT_ONLY`. It does not claim centralized
project vulnerability closure and does not authorize Delivery. LCCoding performs
one independent project security audit after all required Runs are accepted,
coordinates engineering repair and auditor reverification, then performs
Post-Security Owner Acceptance and Delivery governance.

## 19. Completion

A CLK Run completes only when every Required GO and Level is verified, all required
Barriers pass, D3 binds the final candidate and passes, evidence is synchronized,
no blocker or isolation violation remains, and Owner signs
`LOOP_OWNER_ACCEPTED` for the Run product.
