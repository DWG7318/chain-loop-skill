# Run Lifecycle and Verification

## Lifecycle

```text
RUN_CONTRACT_FROZEN
→ CALABASH_AND_CHAIN_LEVEL_BASELINE_FROZEN
→ READINESS_25_OF_25
→ SIMULATION_PASS
→ LEVEL_START_GATE_PASS
→ D0 → D1 → D2 per GO
→ conditional LEVEL Verification
→ LEVEL_BARRIER_PASSED
→ next Level
→ D3 PASS
→ immediate Run Owner Acceptance
→ LOOP_OWNER_ACCEPTED returned to LCCoding
```

Only one Level is open. All listed GO candidates are launch-ready in the same
activation cycle. Different Chains may be active concurrently when workspace,
write scope, resources, rollback, and external-state risk are controlled. Each
Chain has at most one ACTIVE GO.

## Verification economy

D0 proves Worker-side behavior, D1 the CELL Contract, D2 the GO composition, LEVEL
only a new cross-Chain composition claim, and D3 the final Run composition. Each
layer consumes lower signed Receipts and adds only its own claim.

Repeat lower checks only when a candidate or environment changed, evidence expired
or conflicts, composition can change behavior, regression scope expanded, or a
specific new risk requires it. Record the source layer, reason, scope difference,
and result.

For topology faults, the Receipt-consumption graph defines the exact invalidation
and reverification closure. Unrelated healthy-Chain Receipts remain valid. A
Barrier-only correction performs no D0-D3 repetition.

## Fresh attempts

D2, LEVEL, and D3 each use a fresh visible attempt, context, workspace, evidence
directory, and candidate binding. One Verification identity may perform several
layers, but not in a shared attempt or mutable context.

## Level Verification decision

Record a decision for every Level. Verification is mandatory when any of the
following is true:

- cross-Chain data dependency;
- shared mutable-state write;
- multiple GO outputs jointly form one Level claim;
- shared external resource creates coordination risk;
- individual D2 Receipts do not directly prove the Barrier claim.

When none applies, the Supervisor may pass the Barrier mechanically from complete
D2 and terminal Optional evidence. The decision remains auditable.

An unresolved `TOPOLOGY_FAULT_RECORD` for the current Level blocks that pass.
