---
name: chain-loop-skill
description: Use when the user says CLK or Chain Loop Skill, uses the legacy names MSLK or multi-small-loop-skill, or needs fixed persistent Chains advancing through ordered fully synchronized Levels with fresh independent GO Verification. Legacy names normalize to CLK. Never combine CLK with SLK, GLK, or another loop method in one Run.
---

# Chain Loop Skill (CLK)

CLK is the fixed multi-chain, full-Level-barrier execution method. Invoke it as
`$chain-loop-skill`. This file is the always-loaded method kernel; load the linked
reference for the specific operation being performed instead of expanding every
procedure into the activation context.

## Canonical Identity

- Product: `Chain Loop Skill` (`CLK`).
- Repository: `https://github.com/DWG7318/chain-loop-skill`.
- Repository ID: `1298120736`; default branch: `main`.
- Current specification version: `2.6.0`.
- Version source: repository `VERSION` and the matching annotated `v*` tag.
- `MSLK`, `$multi-small-loop-skill`, and the former repository name are historical
  migration identities only. A new formal Run never uses them.

Historical evidence keeps its original identity. Migration creates a new CLK
plan/version, readiness and simulation receipts, role bindings, and append-only ID
mapping; it never rewrites old receipts.

## Scope

CLK represents two or more fixed ownership streams as persistent Chains that move
through ordered synchronization Levels:

```text
Calabash -> frozen RUN_CONTRACT and Chain/Level plan
             |
LEVEL-01: GO-01-A  GO-01-B  GO-01-C
             |        |        |
          Pair A   Pair B   Pair C
             |        |        |
        fresh GO Verification per candidate
             +---- full Level barrier ----+
                              |
LEVEL-02: GO-02-A  GO-02-B  GO-02-C
```

The number denotes the Level and the suffix denotes the Chain. `GO-01-A` is a GO;
`GO-01` alone is not. Peer GOs in one Level are independently launch-ready and
acceptable. The next Level opens only after every required current-Level GO is
`GO_VERIFIED` or has a valid amended optional terminal state.

CLK has no conditional branching, partial unlock, cycles, dynamic Chain creation,
or arbitrary runtime GO routing. Those require GLK. One strict serial stream
requires SLK.

## Method Selection Gate

Select CLK exactly once only when all of the following are provable:

1. at least two `LEVEL-01` GOs can start in the same activation cycle;
2. each is independently acceptable without another peer's unfinished work;
3. mutable write domains and runtime resources cannot invalidate one another;
4. one persistent Checker/Worker pair can own each Chain across later Levels;
5. later work fits ordered Levels with full barriers;
6. no required behavior needs a branch, cycle, partial unlock, dynamic Chain, or
   runtime path choice.

Derive the **最大有效 Chain 数量**: maximize valid stable ownership after Run and
GO granularity are frozen. Resource limits reduce concurrent activation, not the
valid Chain roster. Never inflate the roster by artificial splitting.

Failure is `METHOD_SELECTION_FAILED` or `METHOD_BOUNDARY_EXCEEDED`. Preserve
evidence and stop new formal work; never convert the active Run in place.

Read [Calabash and Chain/Level semantics](references/calabash-and-chain-loop.md)
before planning.

## Hard Rules

1. CLK is the only loop method in the Run.
2. Freeze full Calabash, or Minimum Calabash `Grandpa -> Product Architecture ->
   Ontology`, before formal role launch or Chain/Level planning.
3. Freeze one ordered Level plan and one fixed Chain roster before execution.
4. Use `GO-<LEVEL>-<CHAIN>`; one active Chain has at most one GO per Level.
5. All GOs in an opened Level are independently launch-ready and acceptable; the
   next Level remains closed until the full current barrier passes.
6. Use one persistent Checker/Worker pair per Chain. Never add, replace, skip, or
   resurrect a Chain during the active Run.
7. Formal roles are visible Codex conversations in the same project. Hidden agents,
   subagents, background roles, `spawn_agent`, and `delegate_task` are forbidden.
   A GO, CELL, ROUND, plan step, or visible peer task is a subtask, not a subagent.
8. Bind every role to distinct conversation/context/workspace/runtime/evidence/
   capability/model/lifecycle identities appropriate to its authority.
9. Before a GO's first CELL, freeze its Calabash trace, Verification Contract,
   direct route, environment template, model binding, and fresh Verification attempt.
10. Checker hands the neutral frozen GO package directly to the pre-bound
    Verification instance; Supervisor is not a routine relay.
11. Worker alone edits product artifacts. Checker and Verification never edit and
    accept the same candidate.
12. Checker alone accepts and routes CELL work for its Chain.
13. Fresh Verification alone issues the GO evidence verdict and never plans,
    implements, repairs, routes, or contacts Owner.
14. Supervisor owns Calabash, fixed topology, Level gates/barriers, provisioning,
    cross-Chain control, Owner-exclusive escalation, and final composition audit;
    it signs no CELL or GO verdict.
15. Routine work inside `PROJECT_AUTONOMY_ENVELOPE` proceeds without Owner approval.
16. Only an irreducible Owner-exclusive objective, definition, credential, legal,
    destructive, irreversible, materially costly, physical, or external-account
    matter may reach Owner, and only through Supervisor.
17. Every CELL binds Worker evidence and independent Checker evidence to one exact
    immutable candidate.
18. Every GO binds one current `GO_CALABASH_TRACE`, `GO_VERIFICATION_CONTRACT`, and
    fresh independent Verification verdict.
19. A CELL cannot wait for or consume another GO's unfinished CELL, mutable state,
    or provisional evidence.
20. Cross-GO input comes only from a verified predecessor GO and frozen named output;
    same-Level peer dependency is forbidden.
21. Detection is allocated as `CELL_ALWAYS`, `CELL_TRIGGERED`, `GO_BOUNDARY`, and
    `PROJECT_FINAL`; one layer never impersonates another.
22. Plans, receipts, evidence, verdicts, amendments, and historical decisions are
    append-only; only declared current-state indexes are mutable.
23. Missing roles, stale or partial evidence, silence, timeout, or green Worker
    self-tests never imply acceptance.
24. Completion requires every required GO and Level verified, D3 and composition/
    safety/evidence gates passed, Owner Acceptance, and configured `PROJECT_GOAL`.

Schedule, urgency, model confidence, device capacity, or cost cannot waive a rule.

## Authority

### Supervisor

Supervisor freezes Calabash, `RUN_CONTRACT`, autonomy envelope, Chain roster, Level
plan, cross-Chain contracts, role/model/workspace bindings, Verification templates,
and device-safe budgets. It opens a Level only after `LEVEL_START_GATE_PASS`, records
the deterministic barrier, resolves shared prerequisites and plan defects, governs
safe pause/resume and recovery, and performs the final composition audit.

It does not plan ordinary CELL detail, relay healthy Checker/Verification traffic,
implement, validate a CELL, issue a GO verdict, partially unlock a Level, or perform
GLK routing.

### Checker

One persistent Checker owns one Chain's local solution, GO/CELL plan, contracts,
detection profile, assignments, clean validation, receipts, queue, rework, and direct
Verification handoff. It sends one CELL at a time and routes only:

```text
NEXT | CELL_REWORK | GO_ACCEPTANCE | BLOCKED | PLAN_DEFECT
```

Checker never edits Worker product artifacts, changes Level membership, declares a
GO verified, controls another Chain, or asks Owner for routine confirmation.

### Worker

One persistent Worker executes one assigned CELL or rework round inside the bound
workspace, preserves unrelated changes, produces one immutable candidate plus D0
evidence, and reports completion, blocker, or execution failure. It never selects
the next CELL, broadens scope, changes acceptance, self-accepts, contacts Owner, or
reuses another Worker's evidence.

### Verification

Every planned GO has a pre-bound Verification template. Level activation creates a
fresh visible isolated attempt before the first CELL. It receives only the frozen
contract, candidate, inputs, neutral evidence index, environment, commands, and
safety boundaries. It independently returns to Checker and Supervisor:

```text
GO_VERIFIED | GO_EVIDENCE_GAP | GO_REWORK_REQUIRED
GO_DEFINITION_DEFECT | GO_BLOCKED
```

A material candidate, contract, Calabash, dependency, environment, tool, or rule
change invalidates the verdict and requires a fresh attempt.

Read [role isolation and Verification](references/role-isolation-and-verification.md)
before role launch.

## Execution

### Definition gate and readiness

Supervisor establishes authoritative Calabash without inventing Owner intent.
Irreducible ambiguity is `CALABASH_DEFINITION_BLOCKED`. Every GO traces its outcome
and owned ontology to that baseline; acceptance derives from the trace.

Before formal work, Supervisor and every persistent Checker/Worker pass the current
CLK readiness Eval exactly `25/25`. Every fresh Verification attempt also passes
before receiving a candidate. No partial credit, override, reused receipt, role
substitution, or answer-key access is allowed.

### Simulation and Level start

The project launch simulation is no-side-effect evidence that topology, independence,
role routes, isolation, direct Verification, the full barrier, autonomy, safeguards,
and recovery can execute without hidden roles or GLK behavior. Record only
`SIMULATION_PASS` or `SIMULATION_FAIL`.

Before every Level, `LEVEL_START_GATE_PASS` proves prior barriers, frozen inputs,
same-Level independence, one GO per active Chain, fresh Verification readiness,
contracts, routes, tools, autonomy, model bindings, capacity, and safety. Failure
keeps the whole Level closed.

### CELL and GO flow

```text
Supervisor opens Level
-> Checker assigns GO/CELL/ROUND to its Worker
-> Worker delivers immutable candidate and D0 evidence
-> Checker validates cleanly and signs D1
-> NEXT or bounded Worker-owned CELL_REWORK
-> all GO CELLs D1 accepted
-> Checker freezes GO candidate and neutral package
-> direct fresh Verification
-> signed D2 GO verdict to Checker and Supervisor
-> all required Level members GO_VERIFIED
-> LEVEL_VERIFIED and next Level gate
-> all Levels -> D3 -> Run Owner Acceptance
```

`完成，请检验` means only ready for Checker validation. `DELIVERED` is not
`D1_ACCEPTED`; `GO_CANDIDATE_READY` is not `D2_VERIFIED`.

One Chain may finish rework later than peers; verified peers freeze and wait. No
later Level opens partially. Formal resolution removes or replaces a Required GO
only through a versioned amendment; it never substitutes for required D2.

For exact start, pause, resume, barrier, handoff, and control receipts, read
[CLK control operations](references/clk-control-operations.md). For lifecycle and
verification de-duplication, read [Run lifecycle and Verification](references/run-lifecycle-and-verification.md).

### Detection and rework

Checker maintains a capability manifest and GO detection profile. Worker checks are
inputs, not Checker evidence; Checker evidence is not a GO verdict. `NOT_TRIGGERED`
requires the frozen predicate and evidence.

Product defects return to Worker as a new immutable round. Checker may repair only
Checker-owned validation or coordination infrastructure and cannot alter the product
candidate. Verification never repairs anything.

Read [Checker detection catalog](references/checker-detection-catalog.md).

### Amendments

Historical artifacts are never rewritten. A future GO detail amendment must preserve
the fixed roster, ordered Levels, full barriers, one GO per active Chain per Level,
same-Level independence, Calabash trace, autonomy, and safety. Run delta simulation
before dispatch. Conditional routing, cycles, partial unlock, new Chains, or arbitrary
insertion are `METHOD_BOUNDARY_EXCEEDED`.

## Runtime Safeguards

### Model binding

Every role and Patrol action binds a current immutable `MODEL_BINDING_LEDGER` entry:

- default: `gpt-5.6-terra+xhigh` or proven capability-equivalent model;
- fine-grained LOW-risk Worker CELL explicitly admitted after capacity PASS:
  `gpt-5.6-luna+xhigh` or proven equivalent;
- exceptional high-difficulty correction, diagnosis, or complex rework:
  `gpt-5.6-sol+xhigh` or proven equivalent;
- GPT 5.5 and lower are rejected; `ultra` requires item-specific Owner authorization;
- known Terra/Luna/Sol identities cannot be laundered through equivalence evidence;
- any actual-model or reasoning-effort change creates a new binding, supersession,
  readiness, isolation, and verification evidence. Silent switching fails closed.

Read [model selection and binding](references/model-selection-and-binding.md).

### Worker wake and offline boundary

After dispatch, Checker goes offline. Worker alone wakes the originally bound Checker
using the four-level ladder at `T+0`, `T+2`, `T+4`, and `T+6` minutes, waiting up to
two minutes between attempts. Every message binds GO, CELL ordinal/required total,
dispatch identity, and delivered/blocked/execution-failure state. Preflight must prove
all four wake mechanisms before dispatch. This is not a general message bus.

Supervisor never enters positive `wait_threads`; `timeoutMs: 0` is allowed only as a
non-waiting snapshot.

### Run Patrol

Each Run creates exactly one visible non-authoritative Patrol conversation using the
default model policy. It performs only mechanical checks for unexplained stall,
pending wake, subagent evidence, Supervisor wait, duplicate Patrol/heartbeat, Pin
provenance, and terminal cleanup. Workload interval is LOW 10, MEDIUM 15, HIGH 30
minutes. It never plans, implements, verifies, accepts, routes, reports engineering
progress, or pins/unpins. It ends and archives when terminal completion is evidenced.

### Layered progress

- Worker completion message includes `accepted/required CELL` for its current GO.
- Checker reports current effective D1 accepted CELLs and D2 verified GOs for its
  Chain after each D1 decision and material boundary.
- Supervisor reports verified/required GOs in the Level and completed/required
  Levels after each material trigger.
- Verification reports no continuous progress; Patrol reports no engineering
  progress.

Only current effective signed receipts increment numerators. Required-set amendments
recompute denominators without inventing acceptance. Every D1 decision and material
Supervisor trigger has exactly one bound progress event.

### CELL capacity

Supervisor freezes device capacity and cumulative engineering load. Checker runs a
fresh pre-dispatch `CELL_CAPACITY_GATE`: `PASS`, `SPLIT_REQUIRED`, or
`CAPACITY_BLOCKED`. Unknown capacity blocks. Worker cannot split its own CELL; it
reports `CELL_SCOPE_EXCEEDED`. A post-dispatch split records
`POST_DISPATCH_CELL_SPLIT`; three or more successors are `CELL_OVERSIZE_SEVERE` and
six, seven, or eight are always severe. Later small-looking changes include the
accumulated code, regression, evidence, and context load.

### Pin prohibition and task identity

Only Owner UI action or explicit item-specific Owner authorization may Pin. No CLK
role or Patrol may call `set_thread_pinned`; an agent Pin is
`UNAUTHORIZED_THREAD_PIN`, unknown provenance is `PIN_PROVENANCE_UNKNOWN`, and later
unpinning does not erase the incident. Archiving is independent of Pin state.

For exact wake, Patrol, task/subagent, progress, capacity, and Pin records, read
[Worker wake, Patrol, progress, capacity, and Pin](references/worker-wake-patrol-and-progress.md).

### Topology fault localization

CLK recognizes `CHAIN_LOCAL`, `CROSS_CHAIN_COMPOSITION`, and `LEVEL_BARRIER`. Keep
one active causal hypothesis, bind evidence to content hashes and the source attempt,
prove healthy same-Level controls are comparable, and compute the minimum affected
Receipt-consumption closure. Never substitute healthy evidence for the affected GO.

Native routes remain bounded to Worker/GO rework, Level reverification, or barrier
recalculation. A plan, Calabash, or method-boundary defect stops ordinary repair.
Read [topology fault localization](references/topology-fault-localization.md).

## Evidence and Recovery

Receipts bind contract/baseline/candidate identities, role/context/workspace/model/
capability/environment identities, commands/results, evidence hashes, consumed
receipts, timestamps, and invalidation/supersession state. Current indexes point to
append-only history and never replace it.

Explicitly mutable artifacts are only `WORK_CONTINUATION_INDEX`, the Supervisor
board current-status section, and ephemeral progress cache. Every governed Markdown
file is at most 1000 physical lines; the continuation index stays below 200. Split at
semantic boundaries before overflow and never hard-cut evidence.

Recovery never guesses:

- delayed registration: confirm returned identity before replacement;
- duplicate Checker/Worker: select one authority, stop/archive duplicate, execute
  each CELL once;
- duplicate or contaminated Verification: invalidate and launch one fresh attempt;
- Worker failure: Checker validates usable immutable output or reissues a new round;
- damaged log: seal, link a successor, and revalidate current artifacts;
- missing role/environment: fail closed; never substitute;
- blocked prerequisite: other independent current-Level GOs may continue, but the
  next barrier stays closed.

Read [receipt and state contracts](references/receipt-and-state-contracts.md) for
record structure.

## LCCoding Boundary and Acceptance

CLK consumes a frozen LCCoding `RUN_CONTRACT`; it does not invent product meaning.
It owns Run-local implementation and evidence only. LCCoding retains centralized
security audit, packaging, Delivery, and project completion.

After D3 PASS, Supervisor presents a bounded Run guide. Only explicit Owner verdict
`LOOP_OWNER_ACCEPTED` accepts the Run product. Other outcomes route Run rework,
product-definition change, or a new feature. `PROJECT_GOAL`, when explicitly defined,
adds measurable project-wide evidence but never replaces CELL, GO, Level, D3, or
Owner gates.

Read [LCCoding interface](references/lccoding-interface.md).

## Launch Checklist

Before project launch confirm:

- sole CLK selection and a fixed maximum-valid roster of at least two Chains;
- frozen full/Minimum Calabash and every GO trace;
- ordered Level table using `GO-<LEVEL>-<CHAIN>` with same-Level independence;
- no branch, partial unlock, cycle, dynamic Chain, cross-GO CELL dependency, or GLK
  capability;
- current `25/25` readiness for persistent roles and role templates;
- no-side-effect `SIMULATION_PASS`;
- autonomy envelope, device/cumulative-load profile, and model ledger;
- visible isolated role identities and one persistent Checker/Worker pair per Chain;
- a frozen Verification Contract/binding and fresh direct route for every planned GO;
- detection profiles, append-only evidence, progress, wake, Patrol, capacity, Pin,
  topology-fault, recovery, and final-audit controls.

Before each Level require prior barriers, `LEVEL_START_GATE_PASS`, frozen inputs,
fresh Verification attempts, capacity and isolation PASS, and all first CELLs ready.

Before final closure require every required GO `GO_VERIFIED`, all Levels verified,
current D3, cross-Chain composition and safety PASS, no unresolved blocker or fault,
configured `PROJECT_GOAL` satisfied, final evidence/handoff present, and explicit Run
Owner Acceptance.

## Publication Gate

Before publishing verify owner/name/repository ID, default branch, clean tested
installation, version/Manifest/hash identity, remote main, and new annotated tag.
Never publish CLK content to SLK, GLK, or a legacy repository target. Dynamic graph
behavior remains GLK-only.
