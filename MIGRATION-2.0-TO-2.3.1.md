# Migration From CLK 2.0.0 to 2.3.1

## Stable identity

`Chain Loop Skill`, `CLK`, `$chain-loop-skill`, and `Level` remain canonical.
`Chain Loop Kit` is packaging language only. `Stage` does not replace Level.

## Preserved hard boundaries

2.3.1 retains mandatory Calabash, fixed Chains, ordered full Levels, persistent
Checker/Worker pairs, visible isolated Verification, direct Checker handoff,
Worker-owned rework, Owner-free routine autonomy, append-only evidence, readiness,
simulation, detection tiers, and final composition audit.

## Added contracts

2.3.1 makes cross-Chain concurrency explicit, adds D0-D3 evidence layers,
conditional Level composition Verification, Run-scoped Owner Acceptance, runtime
state, strong Receipt/Amendment envelopes, JSON Schemas, semantic validators, and
negative release tests.

## Historical runs

An active 2.0.0 Run remains bound to 2.0.0. Do not rewrite its Baseline, IDs,
Receipt formats, candidates, or verdicts.

To migrate unfinished work:

1. freeze the last valid 2.0.0 state and evidence index;
2. create a new 2.3.1 Run Contract and Chain/Level Baseline version;
3. append an explicit old-to-new ID and Receipt mapping;
4. bind strong candidate, context, workspace, environment, and evidence identities;
5. run fresh 2.3.1 readiness and simulation;
6. resume only from a previously verified safe Level boundary;
7. create fresh D2/LEVEL/D3 attempts for all new candidates.

No historical `LEVEL-*` identifier is renamed to `STAGE-*`.
