# Receipt and State Contracts

## Strong Receipt binding

Every D0, D1, D2, LEVEL, and D3 Receipt uses the canonical Receipt Envelope. A
Receipt is invalid when its Run, Baseline, Contract, attempt, candidate, context,
workspace/environment, evidence, consumed Receipt, or signer binding is absent or
stale.

Receipt history is append-only. `invalidates` and `supersedes` create explicit
edges; they never delete or rewrite earlier evidence.

## Barrier proof

The Level Barrier Receipt contains the Baseline identity/hash, exact Barrier claim,
Required assignment and D2 Receipt map, Optional terminal-state map, conditional
Level Verification decision and Receipt, candidate-set hash, atomic transition,
Supervisor identity, time, and result.

A still-Required GO accepts only `D2_PASS`. Governance resolution first changes the
Baseline through an Amendment; it is not a technical Receipt substitute.

## Mutable state index

The runtime state index is the only mutable current-state pointer for Run/Level/GO
activation. It references append-only history through `snapshot_id` and
`last_event_id`.

It enforces one open Level, at most one ACTIVE GO per Chain, ACTIVE membership in
the open Level, distinct verification attempt/context/workspace/evidence identities,
and complete Barrier terminal states.

## Amendments

Chain, Level, and GO amendments use one Amendment Envelope. An amendment records
before/after Baseline hashes, authority, reason/evidence, affected attempts and
Receipts, invalidation and reverification, and supersession. Product-definition
changes leave CLK and return to Calabash governance.
