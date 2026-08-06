# Worker Wake, Run Patrol, Layered Progress, Capacity, and Pin Control

## Boundary

This reference owns CLK liveness and progress control only. It adds no technical
role, D layer, product authority, dynamic topology, general message bus, Runtime
state machine, device monitor, or UI-lifecycle authority.

## Worker-only wake ladder

Before formal dispatch, freeze the Worker, paired Checker, Checker thread/host,
Run/Chain/GO/CELL/Round, CELL ordinal, current Required CELL total, and Required-set
version. Preflight all Worker capabilities for send, read, list, unarchive,
temporary-heartbeat upsert/delete, and PENDING_WAKE write. Any missing capability
fails closed before dispatch.

Every active `CELL_DISPATCH` binds exactly one current pair, complete
Run/GO/CELL/Round/Required-set scope, and one wake identity. That identity must
close through success at its reached level or through all three attempts and T+6
PENDING_WAKE. `INITIAL_UNDISPATCHED` may contain no wake; an active dispatch or
Worker signal can never use the empty-trace exception.

Worker uses the ladder only after the current formal CELL delivery, BLOCKED, or
EXECUTION_FAILURE. No other role may use it. The message binds one progress
identity and a short scope:

```text
GO-03-A CELL 25/30 已交付，请检查
```

BLOCKED and EXECUTION_FAILURE keep the same GO/CELL `n/N`. The ordinal is delivery
position, not accepted progress. Rework keeps the ordinal and changes Round only.

| Injected time | Worker action |
|---|---|
| T+0 | Send to frozen Checker thread and host. |
| T+2 | Read/list the original task; unarchive it or resolve the same Checker from the frozen role registry and resend. Never guess identity or create a replacement. |
| T+4 | Upsert one deterministic temporary Checker heartbeat; create no conversation. |
| T+6 | Write one deterministic PENDING_WAKE with all identities, three attempts, errors, and times. Best-effort notification is optional. |

Each level permits at most two injected minutes. Tests use an injected clock and no
real sleep. A matching `WAKE_ACK` or mechanical evidence that the same Checker
started processing stops all later levels. Checker first ACKs Run/GO/CELL/Round,
deletes any temporary heartbeat, then emits:

```text
收到 GO-X CELL n/N，开始检查
```

Success closes or consumes PENDING_WAKE and cannot create duplicate implementation,
validation, Worker, or Checker work.

## Supervisor wait boundary

Supervisor never uses `wait_threads` as a wait, never loops it, and never waits for
all Workers. `timeoutMs: 0` snapshot/read/list observations remain allowed.
Supervisor ends its turn after dispatch or control. Only Worker may perform the
bounded ACK windows above.

## One Run patrol

Each Run has exactly one visible `RUN_PATROL_CONVERSATION` and one heartbeat:

```text
model_binding_id: BINDING::<PATROL>::<VERSION>
model: gpt-5.6-terra
reasoning_effort: xhigh
interval_minutes: 10 | 15 | 30
```

Frozen project workload maps LOW→10, MEDIUM→15, and HIGH→30: a heavy project's
normal silent command window is longer. Patrol is
non-authoritative, performs no product work or technical acceptance, and is not
added to the canonical method-role or D-layer enums.

Patrol checks only:

- unexplained lack of legal progress;
- PENDING_WAKE;
- spawn/delegate/hidden/background Agent evidence;
- Supervisor `wait_threads`;
- duplicate patrol conversation or heartbeat;
- Pin provenance errors;
- patrol left open after formal termination.

Formal PAUSED, legitimate BLOCKED, and documented external-condition wait are not
stalls. Every status binds the complete fixed check set, a fixed status enum, and
evidence identity. Every alert binds a fixed finding, observation identity, and
evidence identity; findings and alerts match one-to-one. Free-form “all normal” is
invalid. Patrol cannot inspect
code quality, judge plans or acceptance, repair, take over, redispatch, report
engineering progress, create/fork/spawn/delegate, Pin, or unpin.

Formal termination order is mandatory:

```text
LOOP_TERMINAL confirmed
→ patrol heartbeat deleted
→ PATROL_CLOSED
→ patrol conversation archived
```

## Task and subagent identity

- Subtask: GO, CELL, Round, plan step, or another scoped work unit.
- Visible peer task: same-project sidebar conversation with stable thread ID; it is
  not a subagent merely because it receives a subtask.
- Subagent: only `spawn_agent`, `delegate_task`, hidden Agent, or background Agent.

Text containing `子任务` is legal. Actual subagent capability evidence is a CLK
violation.

## Hard rule 5: layered real-time progress

### Worker and Checker

Worker delivery never increments acceptance. Checker is the finest progress
authority and derives its numerator from unique, current, effective D1 PASS
Receipts:

- PASS: `GO-X CELL验收 a/N` and next-CELL or candidate state;
- FAIL/REWORK: `a/N` unchanged and same CELL enters a new Round;
- BLOCKED: `a/N` unchanged and blocker shown.

Green Worker tests, delivery, inspection, rework, and duplicate Receipt do not
increment. One Required CELL ID contributes at most once.
Every unique D1 decision is followed by exactly one Checker update bound to that
D1 event, Receipt, current Required-set, and scope. Missing, duplicate, stale,
wrong-trigger, or pre-verdict updates are invalid.

### Checker and Supervisor

Checker sends Supervisor no CELL stream. Only after all current Required CELLs are
D1 accepted does it emit a GO-boundary milestone with GO ordinal/Required GO total,
CELL `N/N`, and one exact state: `GO_CANDIDATE_READY`, `VERIFYING`, or
`D2_VERIFIED`. Candidate ready is not D2 verified.

Supervisor emits one concise update only after substantive GO, Level, frozen
graph/manifest Required-set, Run, D3, or Owner-Acceptance change. It derives:

- current-Level D2-verified Required GOs / current-Level Required GOs;
- verified Levels / total Required Levels;
- current Required-set version and hierarchical state.

Every material trigger has exactly one later Supervisor update bound by event ID.
One trigger cannot cover another; missing, duplicate, reordered, or reused trigger
identity fails closed.

CELL means D1 accepted; GO means D2 verified; Run verified requires D3; Owner
accepted requires the bounded Owner verdict. Verification emits formal verdicts
only. Patrol reports no engineering progress.

### Required-set change

Baseline, manifest, frozen graph, or capacity-split amendment activates a new
versioned Required set and explicitly preserves current Receipt/verdict identities.
All current denominators and numerators are recomputed. Historical progress is not
rewritten. Controlled states are:

```text
DELIVERED
D1_ACCEPTED
GO_CANDIDATE_READY
D2_VERIFIED
RUN_VERIFIED
OWNER_ACCEPTED
```

## Hard rule 6: CELL capacity gate

Before Run/plan freeze, Supervisor freezes a versioned `DEVICE_CAPACITY_PROFILE`
with measured or conservative CPU, available RAM, applicable GPU/VRAM, free disk
and IO, network/external-service limits, processes/ports, safe command concurrency,
observed/conservative command durations, context budget, and evidence budget.
Unknown relevant capability means `CAPACITY_BLOCKED`; vague resource prose is not
evidence.

Supervisor also freezes versioned `CUMULATIVE_ENGINEERING_LOAD` snapshots at Run,
GO, Level, frozen graph/manifest, and measured-feedback boundaries. Snapshots bind
code/dependency/artifact size, full-regression duration, peak memory,
evidence/hash volume, context reload, external-service cost, and cumulative
coupling.

Every CELL estimate covers implementation scope, inputs/dependencies, artifacts,
build/test matrix, independent Checker verification, affected regression,
evidence/hash/cleanup, context, tools/services, rollback/retry, and accepted-baseline
coupling. Total engineering cost, not diff size, drives the gate:

```text
PASS
SPLIT_REQUIRED
CAPACITY_BLOCKED
```

Only current PASS permits dispatch. SPLIT_REQUIRED is resolved before dispatch
into independently deliverable and D1-checkable CELLs with explicit dependencies,
unchanged GO outcome/acceptance, and unchanged verification quality. It creates no
GO, Worker, or agent.

Supervisor owns project device/load and Level device-concurrency budgets. Paired
Checker designs and gates its Chain CELLs within that envelope. Logical same-Level
GO readiness can coexist with safely serialized heavy commands and does not create
a GO dependency.

Measured duration, memory, regression, dependency/artifact, evidence, or context
drift creates a new load version and rechecks every unstarted CELL. Worker that
exceeds a frozen gate emits `CELL_SCOPE_EXCEEDED` with immutable checkpoint/evidence
and stops; it cannot self-split.

Post-dispatch split records `POST_DISPATCH_CELL_SPLIT`. Three or more successors
also records `CELL_OVERSIZE_SEVERE` and reassesses all remaining work plus device
and load budgets. Six, seven, and eight successors are always severe. Split changes
the fifth-rule Required-set version and denominator but not accepted progress.

## Hard rule 7: thread Pin prohibition

Creation, dispatch, ACTIVE, wait, BLOCKED, rework, verification, milestone,
persistence, and project importance never authorize Pin. Every Supervisor,
The canonical Supervisor/Checker/Worker/Verification capability matrix and the
separate patrol binding have `set_thread_pinned: false`. Pin cannot replace registry, status, progress, recovery,
archive, or unarchive.

Only Owner UI action or current-Run item-specific Owner authorization is legal.
Every observed Pin records provenance:

- Owner evidence → allowed;
- Agent/method tool call → `UNAUTHORIZED_THREAD_PIN`;
- unknown → `PIN_PROVENANCE_UNKNOWN` and notify Owner.

Patrol reports but never unpins. Pin followed by unpin retains the original
violation. Unknown provenance is never guessed or automatically changed.

## Machine gate

`run-control-trace.schema.json` and `validate_run_control.py` validate the frozen
bindings and replay injected-time events. They derive wake timing, patrol cleanup,
Pin provenance, capacity result, current Required set, D1/D2 numerators, and
Supervisor counters. The validator uses explicit exceptions rather than Python
`assert`, so normal and `python -O` execution both fail closed.
