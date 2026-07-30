# Migration From CLK 2.3.1 to 2.4.0

## Compatibility

CLK 2.4.0 preserves the 2.3.1 product identity, maximum-valid-Chain definition,
fixed persistent roster, ordered Levels, full Barriers, role authorities, D0/D1/D2/
conditional LEVEL/D3 layers, Receipt binding, amendments, and Run-product Owner
Acceptance boundary.

The new capability is topology fault localization. It adds one append-only record
type and one mutable runtime reference list; it adds no role or verification layer.

Active 2.3.1 Runs remain bound to 2.3.1. Never rewrite their plans, candidates,
Receipts, verdicts, or runtime history to look like 2.4.0 evidence.

## New 2.4.0 requirements

- classify a fault as `CHAIN_LOCAL`, `CROSS_CHAIN_COMPOSITION`, or
  `LEVEL_BARRIER` before rework;
- keep one active hypothesis per fault series and seal falsified records through
  reciprocal supersession;
- bind hypothesis evidence by content hash and the source attempt to its actual
  D0/D1 CELL, D2 GO, LEVEL/BARRIER Level, or D3 Run scope;
- bind exactly one immutable canonical `GO-<LEVEL>-<CHAIN>` Candidate per affected
  Chain;
- bind the concrete issuer identity to explicit responsibility and scope: Checker
  for `CHAIN_LOCAL`, Supervisor for cross-Chain composition and Level Barrier;
- prove comparability before using a healthy same-Level Chain as a control and
  match its preserved catalog D2 ID, hash, and same-Level GO scope;
- require a nonempty Receipt catalog, exact invalidated/preserved partition, and
  exact invalidation and reverification from Receipt consumption;
- enforce legal record-state/hypothesis-status pairs and class-native routes;
- block Barrier PASS while an unresolved current-Level fault exists;
- stop local patching at `PLAN_DEFECT`, `CALABASH_REVIEW_REQUIRED`, or
  `METHOD_BOUNDARY_EXCEEDED` boundaries.

## Migration procedure

1. Stop at a completed Level Barrier; do not migrate during an ACTIVE CELL,
   Verification attempt, or unresolved topology failure.
2. Preserve the 2.3.1 Baseline, runtime snapshot, candidates, Receipts, verdicts,
   and evidence as immutable history.
3. Create a versioned 2.4.0 Run/plan amendment that keeps the same Chain roster,
   Level order, GO ownership, acceptance, and Calabash trace.
4. Add `open_topology_fault_refs: []` to the new runtime index and bind the 2.4.0
   schema, template, Skill, Contract, and readiness hashes.
5. Run fresh 2.4.0 readiness and the existing launch/Level simulations before new
   work. Old readiness receipts are stale for the new Skill hash.
6. Continue only from frozen verified outputs. Any later failure uses a new
   `TOPOLOGY_FAULT_RECORD`; no synthetic record is created for historical defects.

If the migration requires changed product definition, return to Calabash. If it
requires partial unlock, conditional routing, cycles, dynamic Chains, or runtime
path choice, record `METHOD_BOUNDARY_EXCEEDED` and use a separate GLK Run.
