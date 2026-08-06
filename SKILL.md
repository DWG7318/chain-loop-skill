---
name: multi-small-loop-skill
description: Use when the user says MSLK or multi-small-loop-skill, or when one project needs multiple independent, concurrently startable visible Worker conversations with one persistent visible Checker per Worker. Never trigger together with SLK.
---

# Multi Small Loop Skill (MSLK)

Use `MSLK` as the official abbreviation. Keep `$multi-small-loop-skill` as the
Codex invocation name.

## Canonical Identity

- Product name: `Multi Small Loop`.
- Abbreviation: `MSLK`.
- Canonical repository: `https://github.com/DWG7318/multi-small-loop-skill`.
- GitHub repository ID: `1298120736`.
- Default branch: `main`.
- Version source: repository `VERSION` file and matching `v*` tag.

Before publishing an MSLK update, verify the repository owner/name, repository
ID, default branch, and current HEAD. Never publish MSLK changes to the SLK
repository, a compatibility alias repository, or another similarly named skill.

Use one Supervisor to organize and oversee multiple independent Workers.

```text
                         +-> Checker A <-> Worker A
Owner -> Supervisor -----+-> Checker B <-> Worker B
                         +-> Checker C <-> Worker C
```

Each Worker is one persistent execution owner paired with one stable Checker.
The three external roles are always Supervisor, Checker, and Worker.

```text
Project
  -> Checker A <-> Worker A -> GO(s) -> CELL(s)
  -> Checker B <-> Worker B -> GO(s) -> CELL(s)
```

The number of independently acceptable and concurrently startable work units
determines the Worker count and Checker count. Both conditions are strict and
must hold at the same time. GO and CELL counts, project size, or a desire for
speed do not justify multiple Workers.

## Mode Selection Gate

The Supervisor must prove that multiple Workers are necessary during solution
planning, before creating roles.

For every candidate Worker, verify both:

1. Acceptance independence: its result can be inspected and accepted without
   another Worker's future output or evidence, and concurrent writes, state,
   fixtures, tests, or external side effects cannot invalidate that acceptance.
2. Launch independence: its first CELL can be dispatched immediately and does
   not wait for another Worker's future output, decision, or mutation.

These conditions are intentionally difficult. If fewer than two Workers pass
both, record `METHOD_SELECTION_FAILED`, do not launch MSLK, and return the
method decision to the Owner.

## Exclusive Mode Lock

Choose exactly one method before role creation: SLK or MSLK. Once MSLK is
selected for a project run:

- invoke MSLK exactly once;
- do not load, invoke, nest, repeat, alternate with, or switch to SLK;
- do not borrow SLK's combined Supervisor/Checker topology, single-Worker
  behavior, or any other SLK capability;
- do not present SLK and MSLK as interchangeable or generally combinable.

Shared rules never transfer role ownership, topology, messages, state, or
capabilities between MSLK and SLK. Implement every common requirement entirely
inside the selected MSLK role structure. Mentioning SLK for prohibition does not
load it or authorize any of its behavior.

If MSLK is the wrong method or an active plan stops satisfying its gate,
preserve accepted evidence, record `METHOD_SELECTION_FAILED`, stop without new
formal work, and ask the Owner to start a new, separate run with an explicit
method choice. The current run never converts itself into SLK.

## Visible Conversation Only

Every Supervisor, Checker, and Worker role must be a visible Codex conversation
under the same project. Hidden execution is forbidden.

- Never use a subagent, sub-agent, background agent, hidden worker,
  `delegate_task`, or any subagent-dispatch capability.
- Never represent an internal tool call, background job, or invisible execution
  context as a Supervisor, Checker, or Worker.
- Confirm every role conversation belongs to the current project before
  assigning formal work.
- Keep assignments, receipts, repair records, routing, and completion messages in the
  visible project conversations.

### Visible Conversation Lifecycle

- Create or unarchive a role conversation only when an authorized readiness Eval
  or formal task is ready for that role.
- Keep the conversation visible while that task is active.
- Archive it immediately when its authorized work is complete and no formal
  task remains assigned.
- If later work is authorized for the same role in the same project, unarchive
  the existing conversation instead of creating a duplicate.
- Unarchiving a conversation does not repeat the MSLK invocation and does not
  permit SLK activation.
- An archived conversation performs no hidden or background work.

## Mandatory Readiness Eval

Before simulation or formal CELL dispatch, the Supervisor and every persistent
Checker/Worker in the complete frozen roster must pass the
[MSLK question bank](evals/mslk-readiness-questions.json) through the
[`MSLK Eval runner`](scripts/run_mslk_readiness_eval.py). Eval is authorized ready
work; archive a role afterward when no next work is ready.

Every role must score exactly `25/25`. One wrong, missing, extra, or misordered
answer fails the entire attempt. Retry all 25 questions with a new seed after
rereading the cited rules. Partial credit, manual override, inherited receipts,
roster substitution, and answer-key access during an attempt are forbidden.
`MSLK_READINESS_EVAL_PASS` binds release/content hashes, role, pair ID where
applicable, conversation, model/reasoning, seed, attempt, and per-question result.
Any changed identity or content makes it stale and fails closed.

## Mandatory Simulation Gate

Only after current readiness receipts cover the complete frozen roster, run a
no-side-effect simulation before formal work. Planning and simulation may inspect
metadata, but must not edit project files, execute implementation commands, call
external services, create formal role assignments, or start a CELL.

The simulation must:

1. confirm MSLK is the sole selected method and has not been invoked already;
2. model one visible same-project Supervisor plus every visible Checker/Worker
   pair;
3. prove at least two Workers are acceptance-independent and can receive their
   first CELL immediately;
4. rehearse one assignment, delivery, Checker decision, and `NEXT`, `REDO`, or
   `BLOCKED` route per pair;
5. prove no subagent or SLK capability is used;
6. validate ownership, write isolation, canonical Worker workspace binding and pre-authorized CELL operations, evidence paths, model assignments, tests, safety gates, dispatch-then-offline behavior, and role lifecycle;
7. rehearse every Checker's detection capability manifest, CodeGraph baseline,
   and one focused-to-regression evidence route.

Record either `SIMULATION_PASS` with the checked facts or `SIMULATION_FAIL` with
the reason. Formal work requires both current exact-roster readiness receipts and
`SIMULATION_PASS`. A failed or missing gate forbids CELL execution.

## Fresh Role Requirement

Every new project must create fresh visible Worker and Checker conversations
under that same project. Do not reuse roles from another project, even when
their scope looks similar; prior context can contaminate planning, execution,
and acceptance.

Treat "new project" narrowly: reuse is allowed only for a continuation of the
same project identity, objective lineage, coordination records, and evidence
chain. A renamed, copied, adjacent, or merely similar project is new and must
receive fresh roles.

## Model Policy

These MSLK assets are migration-only and cannot authorize a formal new Run. Any
compatibility evaluation uses `gpt-5.6-terra+xhigh`; GPT 5.5 and lower are rejected.
Formal CLK model selection is governed by the canonical
`chain-loop-skill/templates/model-binding-ledger.yaml` and its validator: Terra is
default, while Luna/Sol require their scoped fine-grained or exceptional evidence.
No compatibility record may silently change model or bypass fresh binding gates.

## Role Contract

### Role Authority Matrix

| Responsibility | MSLK owner |
| --- | --- |
| Method gate, project decomposition, cross-Worker contracts, Supervisor board, and final audit | Supervisor |
| Each Worker's initial solution, GO/CELL plan, and evidence-driven GO revision | Its paired Checker |
| CELL assignment, validation, repair, routing, progress display, and per-Worker queue | Its paired Checker |
| Continuation-condition stop, evidence report, and resume validation | Its paired Checker |
| Continuation-condition resolution and Owner-assistance decision | Supervisor |
| Manual start and Owner-configured safe pause/resume control | Supervisor |
| Checker capability, skill, and tool provisioning | Supervisor |
| Detection-system design, execution, calibration, and evidence | Its paired Checker |
| Optional Goal management, gap allocation, and final Goal validation | Supervisor |
| CELL execution | Worker |

MSLK has one distinct Supervisor plus multiple persistent Checker/Worker pairs. It never combines Supervisor and Checker, uses SLK topology, or lets the Supervisor replace ordinary Checker work.

## Owner Assistance Authority
A Worker must never ask the Owner for confirmation, approval, credentials, troubleshooting, or execution help; it solves within authority or sends a formal blocker to its Checker. A Checker must never ask the Owner either; it solves within pair authority or reports a precise condition to the Supervisor. Only the Supervisor may contact the Owner, after exhausting safe authorization repair, provisioning, versioned plan repair, and work-method repair. The Supervisor must minimize Owner assistance and make one specific request only for an Owner-exclusive decision, credential, consent, external action, scope or acceptance change, Goal change, or safety boundary.
## Supervisor Safeguard Patrol
A configured periodic patrol is the last guarantee that work continues. It runs only as the distinct Supervisor and has the highest on-site decision authority within the Owner objective, safety rules, selected MSLK method, and external-action boundaries. It may perform bounded inspection, authorization repair, a versioned plan revision with required simulation, and work-method improvement; it must not execute an ordinary Worker CELL, take over Checker acceptance, or wake a healthy offline Checker merely to inspect an active Worker. Follow [`references/mslk-control-operations.md`](references/mslk-control-operations.md).

### Supervisor

The Supervisor owns the whole project, not the middle of ordinary cell work.

- Translate Owner intent into the overall solution and acceptance target.
- Split the project into mutually independent, concurrently startable Workers.
- Define Worker ownership boundaries and cross-Worker contracts; approve only
  cross-Worker, acceptance, safety, and Owner-decision boundaries of
  Checker-owned plans.
- Create one stable Checker for each Worker.
- Maintain the supervisor board and final result queue.
- Manage manual start and Owner-configured safe pause/same-pair resume control.
- Provision every Checker with authorized skills, Checker-specific tool access,
  permissions, versions, configurations, and a device-safe execution budget.
- Manage and independently validate the optional project Goal completion gate.
- Act as the mandatory Overseer (`监工`) through periodic quick inspections.
- Resolve plan defects, Owner decisions, shared-resource conflicts, and genuine
  blockers that a Checker cannot resolve inside its current authorized plan.
- Perform final local acceptance after a Checker writes a passed result.

The Supervisor must not be the normal relay for Checker/Worker messages or silently take over a Worker's cell.

### Checker

One Checker controls exactly one Worker.

- The Checker owns and maintains its Worker's initial solution, GO map, CELL plan,
  and detailed CELL files.
- Read the complete current versioned plan for its Worker.
- Own its Worker's evidence-driven GO review and revision proposals as part of
  the Checker's planning responsibility.
- Select and package one fixed CELL at a time.
- Send formal tasks directly to its paired Worker as its final online action.
- Stop dispatch and report to the Supervisor when continuation conditions are
  clearly unmet.
- Maintain and execute its Worker's evolving Checker detection system.
- Inspect files, diffs, tests, scans, method logs, and boundaries locally.
- Repair every defect found in its Worker's delivered result; never return a
  repair task to the Worker.
- Route `NEXT`, `REDO`, `COMPLETE`, `BLOCKED`, or `PLAN_DEFECT`.
- Send the next CELL after accepting the current CELL.
- Write the Worker's final passed or blocked queue record.

The Checker may internally perform planning and routing, but it remains one
external role. It must not change GO/CELL scope or acceptance rules ad hoc;
after GO completion it may propose an evidence-driven revision to the
Supervisor under the rule below.

## Checker Detection System

Every Checker must maintain one evolving detection system for its persistent
Worker and ownership domain. The Supervisor must provision every Checker with
mature skills, Checker-specific tool access, permissions, versions,
configurations, and enough device-safe capacity to execute independent
acceptance. A shared tool license or installation does not transfer Checker
authority to the Supervisor or another Checker.

Before formal work, each Checker records `DETECTION_CAPABILITY_MANIFEST` with
available layers, installed skills, executable tools, tool version,
configuration, and omission rationale for unavailable catalog capabilities,
permissions, supported evidence, and compute constraints. This is an availability
inventory, not GO allocation. The Supervisor board indexes every manifest and
confirms cross-Worker compatibility, while each Checker owns its detailed configuration
and evidence. Revalidate the manifest after material tool, architecture,
dependency, ownership, or acceptance changes.

Before defining a GO profile, each Checker reads
[`references/checker-detection-catalog.md`](references/checker-detection-catalog.md)
and verifies its skill/tool catalog against that Checker's manifest. CodeGraph is
mandatory for code or repository work when relevant source can be indexed; the
paired Checker owns its use and evidence.

### GO Detection Profile Contract

Every GO plan must declare one `GO_DETECTION_PROFILE` before simulation or
formal dispatch. The `DETECTION_CAPABILITY_MANIFEST` inventories what is truly
available; the profile allocates what this GO must use. This means skills and
tools are assigned to the GO, never ad hoc to a CELL.

The profile records the GO/version, acceptance risks, every required skill and
tool, skill source, tool version, configuration, and omission rationale for
unselected catalog layers, owning Checker, per-CELL invocation template,
expected result, evidence path, GO-boundary full gate, and device-safe execution
order. The owning Checker writes the profile. The Supervisor provisions and
approves it for capability availability, cross-Worker compatibility, safety,
and resource scheduling. The paired Checker is the sole routine user of the
assigned detection bundle.

Every CELL in that GO must execute every required skill and tool after Worker
delivery and before acceptance. Focused arguments and affected paths may narrow
per CELL, but capability membership may not change. For each
assigned capability it records `CELL_DETECTION_RECEIPT` with version,
configuration, action or command, result, and evidence reference. A real clean,
no-findings, or no-affected-target result after invocation is valid evidence;
`not run`, inherited evidence, and `not applicable` are not.

No required GO-level capability may be skipped. Worker-run checks do not satisfy
this Checker obligation, Supervisor provisioning is not Checker execution, and
another Checker's evidence cannot satisfy the receipt. If a capability is
irrelevant to any CELL, redesign or split the GO before it starts so every CELL
has one coherent detection profile.

Changing the bundle requires a versioned GO plan revision, an updated profile,
and `GO_REVISION_SIMULATION_PASS` before the next CELL is dispatched. The change
applies to every remaining CELL and records whether accepted CELLs require
retroactive revalidation. Never create a one-CELL capability override.

Pin versions/configuration, cache immutable baselines, and use incremental or
differential inputs inside the fixed bundle. Run the complete profile at every
CELL, broader GO-scope inputs at GO acceptance, and every required full gate at
final acceptance. If the computer cannot execute the bundle safely in one pass,
split or serialize the detection commands and reduce CELL size or loop
concurrency, not acceptance quality; complete every receipt before accepting the
CELL. Shared heavy tools may be serialized, but each paired Checker must produce
its own evidence.

The reference defines acceptance-matrix, false-positive, `REGRESSION_EVIDENCE`,
and calibration requirements. They remain mandatory for each paired Checker's
independent acceptance.

If CodeGraph or another required layer, skill, permission, or safe execution
capacity is unavailable, the affected Checker records `CONDITION_BLOCKED`, stops
dispatch, and reports the exact capability gap to the Supervisor. The Supervisor
must provision or safely resolve the shared capability under existing authority,
or request specific Owner assistance. Never substitute a weaker tool silently,
borrow another Checker's evidence, or accept with an incomplete detection system.

## Checker Direct Repair Rule

The Checker must repair every defect found in its Worker's delivered result and
must not send a repair task back to the Worker.

For Checker repair:

- The defect is inside the current CELL's allowed scope.
- The expected correction is unambiguous and small enough to inspect fully.
- The Checker has the tools, permissions, and evidence needed to repair safely.
- The repair does not change the GO/CELL objective, acceptance standard,
  architecture ownership, or Owner decision.
- The repair does not require private credentials, manual Owner action, or an
  unauthorized external side effect.

The Checker must:

1. Preserve the Worker's original delivery and record the detected defect.
2. Make the minimum correction inside the current CELL.
3. Run the same focused and regression checks required for Worker delivery.
4. Record files changed, commands, results, and the route in Checker evidence;
   never rewrite the Worker's append-only method history.
5. Accept the current CELL only after the repaired result passes locally.
6. Send the next formal CELL directly to the Worker.
7. Include a concise `Checker repair update` in that same next-task message:
   previous CELL, defect, Checker fix, and verification result.

The combined repair update and next CELL assignment must be one message whose
first line is the next `Formal task:` heading. Do not send a separate status
message and then leave the Worker without work.

If repair is broad or ambiguous, the Checker splits it into bounded
Checker-owned repair steps. If safe repair exceeds the Checker's authority or
changes the plan, it escalates to the Supervisor as `PLAN_DEFECT`, `BLOCKED`, or
an Owner decision; it never returns the repair to the Worker. If no usable
Worker result exists at all, the original CELL may be re-dispatched as an
original task, not as a repair task. If the repaired CELL was the final CELL,
the Checker writes the final queue instead of inventing another task.

### Worker

One Worker belongs to exactly one Checker.

- Remain the persistent execution thread for the whole assigned work unit.
- Execute every dependency-authorized GO/CELL assigned to that Worker; do not
  create or request a replacement Worker when a GO ends.
- Execute only a formal task from its controlling Checker.
- Work on one CELL at a time and only within the allowed scope.
- Preserve unrelated changes made by other loops or the Owner.
- Maintain append-only method evidence.
- Run required checks and return evidence to the Checker.
- Never self-select the next CELL and never declare its own work accepted.

## Small Loop Protocol

The normal path is direct:

```text
Checker -> Worker -> Checker -> Worker -> ... -> final queue
```

Worker tasks must start with:

```text
Formal task: GO-01/CELL-01.01/R01
```

Checker-owned repair evidence starts with `Repair record:` and is never a
Worker assignment. `REDO` means the Checker repairs and revalidates the
delivery; it does not send correction work back to the Worker. Messages without
the formal task heading are discussion, not executable Worker work.

## Continuation Condition Gate

Before every Worker assignment, the controlling Checker verifies that its
authoritative inputs, dependencies, allowed scope, required tools or credentials,
safety gates, acceptance criteria, and necessary Owner decisions are ready. A
condition is clearly unmet only when evidence identifies the failed prerequisite
and its effect on safe or valid execution.

When a condition is clearly unmet, dispatch closes. The Checker must stop
dispatching formal tasks. It records `CONDITION_BLOCKED` with the Worker, current
GO/CELL, failed condition, evidence, impact, and required outcome, then must
report the condition to the Supervisor. It must not send speculative, filler,
or repair work to the Worker. Archive a Worker that has no active formal task;
its accepted/total count does not increase while blocked.

The Supervisor decides whether Owner assistance is required:

- If resolution requires an Owner-only decision, credential, consent, external
  action, scope change, or acceptance change, record
  `OWNER_ASSISTANCE_REQUIRED`, stop every affected loop, and notify the Owner
  with one specific request plus the evidence and consequence. Do not resume an
  affected Checker until the required response is available.
- If Owner assistance is unnecessary and resolution is within existing
  authority and safety gates, the Supervisor resolves the supervisory condition
  without taking over Checker-owned planning or Worker execution, records
  `SUPERVISOR_RESOLVED` with evidence, records `RESUME_AUTHORIZED`, and must wake
  the same Checker.

After an Owner response, the Supervisor verifies that the response actually
resolves the failed condition, records `OWNER_ASSISTANCE_RECEIVED`, then records
`SUPERVISOR_RESOLVED` and `RESUME_AUTHORIZED` and wakes the same Checker. An
incomplete response leaves every affected loop blocked.

After `RESUME_AUTHORIZED`, dispatch remains closed. The Checker must revalidate
every blocked condition before dispatching a formal task. If any condition still
fails, it keeps `CONDITION_BLOCKED` and reports back to the Supervisor. Never
wake the Worker to probe prerequisites, never wake an unrelated Checker, and
never activate SLK to bypass the block. Unaffected independent Checker/Worker
pairs may continue only when the blocked condition cannot invalidate their
acceptance.

## Mandatory Project Progress Display

Every formal task assignment from a Checker to its Worker must include exactly
one project-wide progress line after the task details:

```text
正在完成 GO-03：35/231
```

The GO identifier is the GO of the newly assigned CELL. The numerator counts
accepted CELLs only across every Checker/Worker pair, after any required Checker
repair and local validation. It is not a per-Worker subtotal. Assigned, running,
delivered-but-unchecked, blocked, revoked, and duplicate CELLs do not count as
complete. Count each accepted CELL identifier exactly once.

The denominator is the total CELL count in the current versioned plan across all
Workers and GO, including accepted historical CELLs and every active remaining
CELL. After an approved GO revision or historical-GO supplement, recompute the
denominator, record the old and new totals in the revision ledger and Supervisor
board, and never reduce it below the accepted count. The numerator never
decreases.

Before every formal task assignment, the Checker recomputes the snapshot from
the project plan and append-only accepted-CELL records and includes it in the
task evidence. The Supervisor remains the sole writer of the Supervisor board
and reconciles those snapshots by CELL identifier. Concurrent Checkers may show
the same point-in-time snapshot, but must never double-count a CELL. Continue
displaying progress until all loops finish. When every CELL is accepted and no
next task exists, the Supervisor's final queue may display the following only
when no Goal is configured or the optional Goal has passed:

```text
全部完成：231/231
```

After finishing a CELL, the Worker must directly send the controlling Checker:

```text
完成，请检验
```

The Worker's final visible reply must also be exactly `完成，请检验`. This
receipt means only "ready for validation". The Checker must still verify the
delivery before routing the next CELL.

Do not actively wait or continuously poll after sending a task or receipt.
Direct delivery should activate the receiving thread.

## Worker, GO, And CELL

Use this canonical hierarchy only:

```text
Project -> independent Worker/Checker -> GO -> CELL
```

- Worker: one persistent execution owner with an independent work domain.
- Checker: the persistent planning, validation, and routing role paired to that
  Worker.
- GO: a verifiable outcome within the Worker, not a phase, wave, or thread.
- CELL: the smallest inspectable work package inside one GO.
- Round: `GO-01/CELL-01.01/R01`.

A Worker is valid only when both conditions hold:

1. Independence: it can receive its own GO/CELL tasks and produce results that
   can be inspected and accepted without borrowing another Worker's evidence
   or suffering acceptance interference from concurrent writes or side effects.
2. Parallel start: its first CELL has no prerequisite on another Worker's
   future output, so all Workers in the active MSLK can start together.

Never renumber GO/CELL after launch.

### Derive Worker Count Correctly

1. Identify materially independent work units by ownership, authoritative
   files, contracts, and side effects.
2. Confirm every candidate Worker can start now and be accepted independently.
3. Create exactly one Worker and one Checker for each valid work unit.
4. Assign one or more GO to each persistent Worker.
5. Count Workers from independent, concurrently startable work units, never
   from GO count, CELL count, schedules,
   dependency depth, phases, waves, or desired visual symmetry.
6. Keep the same Worker when one assigned GO ends and the next assigned GO
   is an internal continuation owned by the same Worker.
7. At launch, every created Worker must have a dependency-ready first CELL
   that can be dispatched immediately.
8. If Worker B must wait for Worker A's future output, B is not a valid Worker
   in the current MSLK. Do not create B, its Checker, or an Overseer row yet.
9. If only one candidate remains valid, record `METHOD_SELECTION_FAILED`, stop
   MSLK launch, and return the method decision to the Owner.

Do not invent stages or waves unless the Owner explicitly asks for them. GO
dependencies are sufficient to determine when a Checker may dispatch a CELL.

### Required Assignment Table

Before launch, produce one machine-checkable table:

```text
| Worker | Checker | Assigned GO | GO count | CELL count |
```

Validate all of these:

- Worker count = Checker count.
- Every GO is assigned exactly once.
- Every CELL is assigned exactly once through its GO.
- Sum of per-Worker GO counts equals the project GO count.
- Sum of per-Worker CELL counts equals the project CELL count.
- Each Worker has one direct receipt target: its controlling Checker.
- Method-log and final-queue names are unique per Worker.

### Design GO

- Define GO as a verifiable outcome owned by one Worker.
- GO scope follows project need and must not be reduced for device capacity.
- Let one Worker own multiple related GO when they share the same write domain.
- Express ordering as GO dependencies; do not create another project layer.
- Keep GO changes versioned and evidence-driven; route every revision through
  the Supervisor.
- Do not distribute GO evenly merely to make Worker totals look symmetrical.

### Evidence-Driven GO Revision

After every GO is completed and checked, its Checker compares the accepted plan
with the actual result, including delivered scope, defects, residual risk, new
dependencies, changed estimates, and incomplete outcomes.

The Checker owns the resulting GO revision proposal and may:

- adjust any subsequent GO that has not started;
- add a supplementary GO for a historical GO when the completed result exposes
  missing, corrective, or follow-up work;
- revise affected CELL maps, dependencies, model assignments, and the Worker
  assignment table.

The Checker sends the proposal and evidence to the Supervisor. The Supervisor
may approve, reject, or return it for revision based on cross-Worker dependency,
ownership, acceptance, safety, or Owner-decision boundaries, but must not author
ordinary GO revisions in place of the Checker. The Worker must not revise GO or
CELL plans.

GO revision is append-only and versioned:

- never rewrite the historical GO, its evidence, or its acceptance result;
- retain existing identifiers and add a revision or supplement identifier such
  as `GO-03-R1` or `GO-03-S1`;
- keep a historical-GO supplement with the same owning Worker unless the Owner
  explicitly authorizes a new project run;
- do not create an extra Worker or Checker merely because a GO changed;
- record the triggering evidence, reason, old/new scope, dependencies,
  acceptance criteria, affected CELLs, and Owner decision when required;
- preserve MSLK acceptance independence, parallel safety, method exclusivity,
  visible-conversation rules, and existing safety gates.

Before dispatching a revised or supplementary GO, run a no-side-effect delta
simulation for every affected Checker/Worker pair and record
`GO_REVISION_SIMULATION_PASS`. Without that record, the revision remains
proposed and no formal CELL may start.

### Design CELL

Every CELL must define:

- objective;
- authoritative inputs;
- allowed write scope;
- forbidden scope;
- output artifacts;
- focused checks and broader regression;
- evidence and append-only method log;
- dependencies;
- Worker model and reasoning assignment;
- its GO detection-profile reference and `CELL_DETECTION_RECEIPT` path;
- completion criteria.

Size CELLs by implementation risk, cross-owner impact, and evidence burden.
CELL size must be kept modest enough for the current computer to execute and
verify reliably. Reduce files touched, command fan-out, runtime, and evidence
volume when device capacity is limited. Split the same GO into more CELLs rather
than shrinking the GO or weakening acceptance. Uneven CELL counts are expected.
A Worker still executes one CELL at a time.

Before launching a Worker, its Checker must provide:

1. A solution file with objective, boundaries, architecture, risks, and
   acceptance.
2. A GO file with outcomes and dependencies.
3. A CELL index plus one detailed CELL file per GO.
4. The Worker/Checker assignment and exact GO/CELL totals.
5. One `GO_DETECTION_PROFILE` inside the plan for every GO.

## Multi-Worker Decomposition

Use MSLK only when Workers are materially independent and concurrently
startable.

Independence is a launch-time execution property, not a future intention. All
Workers in one active MSLK must be dependency-ready and independently
executable when the MSLK starts. A different write directory or business name
does not make a Worker independent if its first CELL still needs another
active Worker's future output.

For every Worker:

- Assign one unique business/module/write-domain owner.
- Assign one persistent Checker and one persistent Worker.
- Use distinct method logs and final queue names.
- Define disjoint write scopes or explicit shared-file serialization.
- Define cross-Worker contracts as refs/events/interfaces rather than informal
  assumptions.
- Keep one Worker's completion evidence separate from every other Worker.

Do not run Workers concurrently against the same authoritative files without a
declared serialization or merge policy. If a shared dependency blocks several
Workers, the Supervisor resolves it once and authorizes the affected Checkers.

Do not create idle Workers for later dependent work. Resolve cross-Worker
dependencies in exactly one of these ways:

1. Merge the dependent GO into the same persistent Worker.
2. Complete and freeze the shared prerequisite with one loop before launching
   the independent MSLK Workers.
3. Defer the dependent work until its prerequisites pass Supervisor acceptance;
   the Owner must explicitly choose the method for a separate future run.

### Dependency-Waiting Anti-Pattern

This is invalid:

```text
Worker A: starts GO-01 now
Worker B: created now, waits for Worker A to finish GO-01
Worker C: created now, waits for Worker B to finish
```

Only Worker A exists as executable work. B and C are future assignments, not
parallel Workers. Labeling them `waiting_for_go_dependency`, pre-creating their
threads, or counting them in the current Worker total does not make the launch
parallel. Stop the launch as `PLAN_DEFECT`, archive or revoke the premature
pairs, finish/freeze the prerequisite, and recalculate Worker count from the
Workers that can start immediately.

The number of GO and CELL does not need to be equal between Workers. Allocate
them according to ownership, complexity, risk, dependencies, and evidence.

## Pre-Authorized Worker Execution Gate

Before dispatch, the Supervisor provisions the pair and the Checker records `WORKER_EXECUTION_GATE_PASS`: the assignment's canonical workspace path must exactly match the Worker's bound conversation workspace, and the Checker must pre-authorize every routine operation inside the CELL allowlist. Routine approval must never be delegated to the Owner; an unexpected prompt is `WORKER_EXECUTION_FAILURE`. Credentials, external side effects, destructive or security-sensitive work, out-of-allowlist writes, and scope, acceptance, or Goal changes remain an Owner-only decision. Follow the detailed gate in [`references/mslk-control-operations.md`](references/mslk-control-operations.md).

## Dispatch-Then-Offline Boundary
Before dispatch, the Checker completes every check, record, snapshot, and message. The formal Worker assignment is the Checker's final action and enters `OFFLINE_WAITING_WORKER_SIGNAL`; the Checker must immediately end its turn and go offline, and must not poll, inspect, run status, perform oversight, or do more pair work while its Worker owns the CELL.
Only `WORKER_COMPLETION_RECEIPT`, `WORKER_BLOCKER_RECEIPT`, or `WORKER_EXECUTION_FAILURE` may wake that Checker; its next assignment repeats the boundary. Distinct Supervisor safeguard patrol continues independently but never wakes or uses a healthy offline Checker merely to inspect an active Worker.

## MSLK Control Commands

Before every inspection or control action, read
[`references/mslk-control-operations.md`](references/mslk-control-operations.md)
and its machine-readable
[`contracts/mslk-control-kernel.json`](contracts/mslk-control-kernel.json).
`MSLK START` is manual only and authorizes the complete prepared frozen roster.
Timed control only pauses or resumes existing pairs at safe CELL boundaries; it
never adds, replaces, or pre-creates a pair. A paused pair is not complete.
Every command records an idempotent `MSLK_CONTROL_RECEIPT` with project-wide
progress and explicit per-pair results. The Supervisor must not interrupt an
active CELL and must wake the same Checker for resume revalidation.

## Optional Goal Gate

The Owner may define one optional Goal. A Goal is active only when the Owner
explicitly supplies or approves its identifier, objective, measurable success
criteria, required evidence, and safety boundaries. The Supervisor must not
invent, broaden, or silently change it. Owner-authorized Goal changes are
versioned and append-only.

If no Goal is configured, ordinary MSLK acceptance applies. An untested Goal or
`GOAL_GAP` remains unfinished Supervisor work.

Checker completion is provisional. Every controlling Checker must first accept
the current PLAN/GO/CELL work and submit its passed queue. The Supervisor must
independently validate the Goal against fresh project-wide evidence:

- record `GOAL_SATISFIED` only when every Goal criterion is proven;
- otherwise record `GOAL_GAP` with each unmet criterion, evidence, residual
  risk, affected ownership domains, and required outcome;
- while `GOAL_GAP` exists, the Supervisor must not declare project completion or
  write the final passed queue.

After `GOAL_GAP`, the Supervisor allocates each missing outcome to the existing
independent ownership domains. Each affected Checker designs its own
PLAN/GO/CELL continuation for its persistent Worker. The Supervisor must not
author those detailed Checker plans; it approves only cross-Worker, acceptance,
safety, and Owner-decision boundaries.
Each Checker preserves accepted history, appends new identifiers, and obtains
`GO_REVISION_SIMULATION_PASS` before dispatching new CELLs. Recompute the
project-wide denominator, unarchive roles only when formal work is ready, and
continue until the Supervisor records `GOAL_SATISFIED`.

If the Goal gap cannot preserve MSLK acceptance and launch independence, or
cannot proceed within Owner authority, safety gates, or available evidence,
record `METHOD_SELECTION_FAILED`, `BLOCKED`, `PLAN_DEFECT`, or an Owner decision.
Do not claim completion, combine SLK, or switch methods inside the current run.

## Markdown Context Boundary

Every Markdown file governed by the loop has a hard maximum of 1000 physical
lines, counting blank lines and fenced content. This is a Codex
context-readability limit, not a device-capacity limit. A stronger computer,
model, or context window does not waive it.

Governed files include every solution, plan, GO, CELL, manifest, profile, index,
log, receipt, evidence, queue, coordination file, and other Markdown created or
materially expanded by the loop. Existing read-only source or third-party Markdown is not
governed until a Checker plan requires modifying it; then the Supervisor must
authorize a semantic split or record `PLAN_DEFECT`/`CONDITION_BLOCKED`.

During solution design, the Supervisor defines the artifact map, sharding policy,
and `WORK_CONTINUATION_INDEX`. The index is a bounded mutable current-state
pointer below 200 physical lines, not append-only history. It records plan,
active shard/pair/GO/CELL, invariants, blockers, latest evidence, and next action.
Historical detail remains in linked semantic shards.

Prefer multiple files that follow how work continues and split at a semantic
work-continuation boundary such as a Worker domain, GO, coherent CELL group,
completed decision, evidence batch, or execution phase. The split must not
hard-cut a requirement, table, code block, acceptance record, or evidence chain.
Each successor names its predecessor, continuation reason, carried invariants,
owning Checker, and next action; update the index before continuing.

Any GO that can write Markdown must assign `markdown-line-budget` in its
`GO_DETECTION_PROFILE`. Every CELL acceptance checks all created or materially
expanded Markdown files and records `MD_LINE_BUDGET_PASS` with paths and physical
line counts. Before the next append would exceed 1000 lines, close the current
file at the nearest semantic boundary and continue in a linked file. Never delete
required detail or compress evidence merely to pass the limit.

After context compaction or a shard transition, the Supervisor and affected
Checker reload the `WORK_CONTINUATION_INDEX`, current semantic file, predecessor
handoff, governing GO profile, and latest accepted evidence before routing work.
If a valid split cannot be made within scope or format constraints, stop affected
dispatch rather than accepting an unreadable or misleading Markdown artifact.

## Evidence And Queue

Use project-local coordination paths unless the project defines others:

```text
coordination/
  plans/
  checker-messages/
  worker-method-logs/
  supervisor-board.md
```

Method logs are append-only. Rotate before the next append would exceed 1000
lines or when an old shard must be sealed; never rewrite history to make evidence
look clean. Every new shard cites the prior shard and its hash.

Only the Checker writes a final Worker record:

```text
MSLK_YYYYMMDD-HHMMSS_<worker>_<plan-version>_<result>.md
```

Valid results are `passed`, `blocked`, `plan-defect`, `owner-decision`, and
`stopped`. A Worker is complete only after the passed record exists and the
Supervisor's final audit accepts it. Project completion with a configured Goal
also requires `GOAL_SATISFIED`.

No governed planning, log, queue, or coordination Markdown file may exceed 1000
lines. Split rather than remove necessary detail.

## Recovery Rules

- Delayed thread registration: confirm a returned thread ID with `read_thread`
  before creating a replacement; temporary list/title failure does not prove
  creation failed.
- Duplicate Checker: choose one controlling Checker, stop/archive the other,
  and ensure the Worker executes each CELL once.
- Thread `systemError`: Checker inspects and repairs usable partial outputs; only
  when none exist may it re-dispatch the original CELL unchanged.
- Damaged method log: seal it, authorize a new shard, preserve the incident,
  and revalidate current artifacts without fabricating history.
- Dynamic shared data: distinguish legitimate external drift from writes by
  the current CELL through short-window semantic and writer-attribution checks;
  do not chase perpetual fixed hashes.
- Repeated same defect: Checker continues bounded Checker-owned repair and
  escalates a real plan defect or blocker to the Supervisor; it never sends the
  correction back to the Worker.

## Launch Checklist

Before launching multiple loops, the Supervisor confirms:

- Current `MSLK_READINESS_EVAL_PASS` receipts prove exactly `25/25` for every
  role in the complete frozen roster.
- `SIMULATION_PASS` exists for this exact plan and role roster.
- MSLK is the sole method, was invoked once, and no SLK capability is present.
- Every role is a visible conversation under the same project; no subagent,
  hidden worker, or background agent exists.
- Every role conversation has work ready, and every no-work conversation is
  archived with an explicit unarchive path for later same-project work.
- Each Worker has complete solution/GO/CELL plans.
- The artifact map and current-state `WORK_CONTINUATION_INDEX` below 200 physical
  lines cover every Checker domain; every governed file is at most 1000 lines.
- The GO revision ledger is present; every completed GO has an evidence review,
  and every revised or supplementary GO has `GO_REVISION_SIMULATION_PASS`.
- Every created Worker's first CELL is dependency-ready and can be dispatched
  immediately in the launch turn.
- No Worker needs another active Worker's future output to begin or continue its
  current authorized work.
- Ownership and write scopes do not collide.
- Every Checker/Worker pair and receipt target is correct.
- Method-log and final-queue paths are unique.
- Tests, scans, safety boundaries, and external-action gates are explicit.
- Every Checker has a versioned `DETECTION_CAPABILITY_MANIFEST`, mature detection
  skills, Checker-specific tool access, and an acceptance matrix for its domain.
- Every GO has a Checker-authored, Supervisor-approved `GO_DETECTION_PROFILE`;
  every CELL references it and requires that paired Checker's complete
  `CELL_DETECTION_RECEIPT` before acceptance.
- Every GO that can write Markdown includes `markdown-line-budget`, and every
  accepted CELL has paired-Checker `MD_LINE_BUDGET_PASS` evidence.
- CodeGraph has produced each code/repository domain's current structural
  baseline; required native checks and task-relevant Semgrep/CodeQL, Gitleaks,
  OSV-Scanner/Trivy, Playwright, coverage/mutation, and API/schema layers are
  assigned at GO level and provisioned, or are excluded from that GO with an
  approved plan-level rationale before any CELL starts.
- Every compatibility CELL declares an explicit model binding and reasoning level.
- Compatibility readiness uses `gpt-5.6-terra xhigh`; GPT 5.5 and lower are
  rejection cases, and formal model exceptions belong only to canonical CLK.
- GO scope follows project need; every CELL is sized for reliable execution on
  the current computer without weakening GO acceptance.
- Every Checker task displays project-wide `正在完成 GO-NN：accepted/total`, and
  the Supervisor final queue displays `全部完成：total/total`.
- Every assignment has passed the continuation-condition gate; any
  `CONDITION_BLOCKED` record has either active Owner assistance or a verified
  `SUPERVISOR_RESOLVED` plus `RESUME_AUTHORIZED` sequence.
- The optional Goal is either absent or explicitly defined; a configured Goal
  blocks project completion until the Supervisor records `GOAL_SATISFIED`.
- The supervisor board lists every Worker and its persistent Checker.
- Any safe pause or same-pair resume is Owner-configured, versioned, scoped, and
  uses the MSLK command contract.
- Every Checker assignment is its final online action and leaves that Checker in
  `OFFLINE_WAITING_WORKER_SIGNAL` until a completion, blocker, or failure signal.
- Supervisor oversight never wakes a Checker merely to inspect an active Worker.
- No Worker relies on another Worker's passed record as its own evidence.
- The role authority matrix is unchanged; no SLK combined role, single-Worker
  behavior, state, or message route has been borrowed.

Then record manual `MSLK START`; each Checker sends its first CELL as its final
online action. The Supervisor remains outside ordinary Checker/Worker traffic.
