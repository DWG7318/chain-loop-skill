# Changelog

## 2.5.0

- Added the Worker-only T+0/T+2/T+4/T+6 wake ladder for its frozen Checker,
  scoped delivery messages, `WAKE_ACK`, temporary heartbeat, and `PENDING_WAKE`.
- Prohibited Supervisor `wait_threads` waiting and added exactly one mechanical
  Luna+xhigh Run patrol with deterministic terminal cleanup.
- Distinguished GO/CELL/Round subtasks, visible peer tasks, and forbidden spawned,
  delegated, hidden, or background subagents.
- Added receipt-derived layered progress: Worker delivery, Checker D1 acceptance,
  and Supervisor D2/Level/Run milestones with versioned Required denominators.
- Added versioned device-capacity/cumulative-load facts and a fail-closed
  pre-dispatch CELL capacity gate, including severe post-dispatch split feedback.
- Denied task-Pin capability to every method role and added Owner/Agent/unknown
  provenance handling without automatic unpin.
- Added a closed run-control schema/template, semantic validator, readiness and
  optimized-mode negative tests, CI gate, migration guide, and release evidence.

## 2.4.0

- Clarified that CLK derives the `最大有效 Chain 数量` after Run/GO granularity
  freezes; resource limits affect ACTIVE concurrency, not the fixed roster.
- Added append-only topology fault localization for `CHAIN_LOCAL`,
  `CROSS_CHAIN_COMPOSITION`, and `LEVEL_BARRIER` without adding a role or D layer.
- Enforced one active hypothesis per fault series, proven comparability for healthy
  same-Level Chain controls, and no D2 substitution or peer dependency.
- Added Receipt-consumption-derived minimal invalidation/reverification closure and
  Barrier-only recalculation semantics.
- Hardened cross-field binding for nonempty Receipt partitions, hashed hypothesis
  evidence, source attempt scope, healthy-control D2 identity, state, and route.
- Anchored one immutable Candidate per affected Chain to canonical Level/Chain GO
  identity and bound issuers to existing Checker/Supervisor responsibility scopes.
- Added explicit `PLAN_DEFECT`, `CALABASH_REVIEW_REQUIRED`, and
  `METHOD_BOUNDARY_EXCEEDED` escalation boundaries plus runtime Barrier blocking.

## 2.3.1

- Preserved `Chain Loop Skill` and `Level` as the canonical product identity and
  synchronization unit.
- Made true cross-Chain concurrency explicit while retaining one ACTIVE GO per
  Chain and a full Level barrier.
- Added D0, D1, D2, conditional Level composition Verification, and D3 with
  receipt-consumption de-duplication.
- Closed the formal-resolution and unresolved-Optional Barrier bypasses.
- Added strong Receipt and Amendment envelopes, runtime state, immutable candidate
  binding, schemas, templates, and fresh verification context/workspace evidence.
- Added negative topology/state tests, repository/hash validation, explicit CI
  dependencies, complete MIT licensing, and 2.0.0-to-2.3.1 migration guidance.
- Defined `LOOP_OWNER_ACCEPTED` as immediate Run-product acceptance while project
  security closure and Delivery remain LCCoding responsibilities.

## 2.0.0

- Renamed Multi Small Loop Skill (MSLK) to Chain Loop Skill (CLK).
- Changed canonical invocation to `$chain-loop-skill` and skill folder to
  `chain-loop-skill/`.
- Renamed contract, readiness Eval, runner, control commands, receipts, and release
  artifacts from MSLK prefixes to CLK prefixes.
- Preserved fixed Chain, ordered Level, full barrier, Calabash, Verification,
  autonomy, isolation, GO-boundary, and tiered-detection semantics.
- Added append-only migration rules for historical MSLK runs and repository/folder
  rename instructions.
