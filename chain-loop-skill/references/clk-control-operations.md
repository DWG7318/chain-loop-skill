# CLK Control Operations

## Manual project start

`CLK START` authorizes the frozen Calabash baseline, persistent Chain roster,
ordered Level plan, autonomy envelope, and Level-01 activation preparation. It does
not require Owner approval for each CELL, GO, Verification, or later Level.

## Level activation

Before opening one Level, Supervisor:

1. verifies every prior Level is `LEVEL_VERIFIED`;
2. verifies all listed GOs are launch-ready together;
3. confirms no peer GO dependency exists;
4. creates every GO's fresh Verification attempt;
5. binds isolated environments, model identities, evidence paths, and direct routes;
6. obtains role readiness and Verification preflight;
7. freezes current device/load facts and requires PASS capacity gates;
8. records `LEVEL_START_GATE_PASS` and authorizes first CELL dispatch together.

No partial Level start is allowed.

## Direct Verification handoff

After a Checker accepts all CELLs, it sends the frozen neutral package directly to
the pre-established Verification. Supervisor must not relay, rewrite, summarize, or
add a verdict suggestion.

Verification sends its signed verdict directly to Checker and Supervisor. Checker
handles evidence work or Worker rework. Supervisor updates GO/Level state and handles
only plan, shared, safety, autonomy, or Owner-exclusive issues.

## Level barrier

Verified early GOs freeze outputs and wait. The next Level opens only after all
required current-Level GOs are `GO_VERIFIED`, at which point Supervisor records
`LEVEL_VERIFIED` and runs the next Level start gate.

## Safe pause

Pause new dispatch at a CELL or GO-verdict boundary. Do not interrupt an active
Worker or Verification. A pause is not acceptance and does not open a later Level.

## Resume

Supervisor records `RESUME_AUTHORIZED`. The same persistent Checker revalidates
conditions; a changed GO candidate uses a new Verification attempt. Resume never
requires routine Owner approval.

## Wake and mechanical patrol

Worker alone may use the four-level bounded ladder to wake its frozen Checker.
Every active dispatch binds one same-scope lifecycle; only an explicit initial
undispatched trace can contain no wake or Worker signal.
Supervisor finishes its control turn and never waits through `wait_threads`. Each
Run has exactly one visible Luna+xhigh patrol and one heartbeat; patrol reports
mechanical faults through fixed check/status/finding and observation/evidence
identity. Project workload maps LOW→10, MEDIUM→15, HIGH→30 minutes. Patrol never accepts, repairs, dispatches, takes
over, Pins, or reports engineering progress. See
[`worker-wake-patrol-and-progress.md`](worker-wake-patrol-and-progress.md).

The four canonical technical roles lack task-Pin capability; patrol is separate
and also Pin-denied. Patrol classifies evidenced Agent Pin as
`UNAUTHORIZED_THREAD_PIN` and unknown provenance as `PIN_PROVENANCE_UNKNOWN`, but
never unpins. Owner-explicit Pin remains valid and lifecycle-independent.

## Owner-free autonomy

`PROJECT_AUTONOMY_ENVELOPE` pre-authorizes routine plan-scoped work. Only Supervisor
may emit `OWNER_ASSISTANCE_REQUIRED`, and only for one proven Owner-exclusive item.
A generic confirmation request is `AUTONOMY_VIOLATION`.

Platform permission friction is first handled by provisioning/preauthorization. If
unavoidable, record `EXECUTION_PERMISSION_BLOCKED` with exact evidence.

## Control receipts

Every control action records an idempotent receipt with Calabash/plan/Required-set
version, Level, Chain and role IDs, candidate identity where relevant, old/new
state, evidence, and result.
