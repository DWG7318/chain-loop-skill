# Chain Loop Skill (CLK)

CLK executes one bounded engineering Run as fixed persistent Chains advancing
through ordered, fully synchronized Levels with independently bound evidence.

Canonical product name: `Chain Loop Skill`

Canonical repository: `DWG7318/chain-loop-skill`

GitHub repository ID: `1298120736`

Current version: **2.3.1**

## Definition and input

Every Run starts from a frozen `RUN_CONTRACT` and Full or Minimum Calabash:

```text
Grandpa → Product Architecture → Ontology
```

Every GO has a current `GO_CALABASH_TRACE`, one primary engineering claim, a
frozen Verification Contract, and an immutable candidate-binding policy.

## Chain and Level topology

```text
              CHAIN-A      CHAIN-B      CHAIN-C
LEVEL-01      GO-01-A      GO-01-B      GO-01-C
                 ↓            ↓            ↓
                 D2           D2           D2
                 └──────── full Level barrier ────────┘
                                      ↓
LEVEL-02      GO-02-A      GO-02-B      GO-02-C
```

The numeric GO component identifies the Level; the suffix identifies the Chain.
All members of an opened Level are launch-ready together. Multiple GOs may be
ACTIVE across different Chains, but each Chain has at most one ACTIVE GO. The next
Level stays closed until the complete current-Level Barrier passes.

The roster uses the `最大有效 Chain 数量`: after Run and GO granularity is frozen,
select the largest valid Chain partition that preserves ownership, cohesion,
same-Level launch and acceptance independence, write isolation, local order, and
full-Run Level barriers. Runtime resources may reduce ACTIVE concurrency, but do
not change that frozen roster.

Use SLK for one strict execution line. Use GLK for conditional branches, partial
unlock, cycles, dynamic Chains, or arbitrary GO-to-GO routing.

## Evidence layers

- D0: Worker implementation evidence.
- D1: Checker verdict on one immutable CELL candidate.
- D2: fresh Verification verdict that accepted CELLs compose one GO claim.
- LEVEL: fresh composition Verification only when D2 receipts do not prove a new
  cross-Chain Level claim.
- D3: fresh Verification that all verified Levels compose the frozen Run Feature.

Higher layers consume signed lower receipts. They do not blindly repeat lower
checks. Candidate, contract, baseline, environment, evidence, or risk changes can
require a new attempt.

## Barrier safety

A Required GO that remains in the frozen Baseline must have D2 PASS. A governance
resolution cannot substitute for that technical verdict; an amendment must first
remove, cancel, or supersede the GO.

An Optional GO may finish without D2 PASS only by reaching a declared non-active
terminal state such as `CANCELLED`, `DEFERRED_BY_AMENDMENT`, or `SUPERSEDED`.
ACTIVE, pending, or unresolved Optional work blocks the Barrier.

## Isolation and authority

- Supervisor controls Calabash, planning, provisioning, Barriers, amendments, and
  Owner-exclusive escalation; it signs no product technical verdict.
- Worker owns product implementation and rework.
- Checker accepts CELLs and routes its persistent Chain.
- Fresh Verification attempts sign D2, conditional LEVEL, and D3 receipts.

D2, LEVEL, and D3 require distinct attempt, context, workspace, candidate binding,
and evidence identities even when one independent Verification identity performs
all three layers.

## Owner acceptance and outer boundary

After D3 PASS, CLK immediately facilitates the current Run's small Owner
Acceptance. `LOOP_OWNER_ACCEPTED` means `RUN_PRODUCT_ONLY`; it does not mean that
project security is closed or Delivery is authorized.

LCCoding remains responsible for centralized project vulnerability audit,
Post-Security Owner Acceptance, and Delivery after all required Runs are accepted.

## Repository gates

```text
python scripts/validate_repository.py
python scripts/validate_chain_level_plan.py tests/fixtures/plans/valid-minimal.yaml
python scripts/validate_runtime_state.py tests/fixtures/runtime/valid-level-active.yaml
python scripts/validate_receipt_chain.py chain-loop-skill/templates/d0-worker-receipt.yaml chain-loop-skill/templates/d1-checker-receipt.yaml chain-loop-skill/templates/d2-go-verification-receipt.yaml
python -m pytest -q
```

## Install

Install `chain-loop-skill/` and invoke:

```text
$chain-loop-skill
```

Historical MSLK artifacts at repository root remain migration evidence only. New
runs use `CLK`, `Chain Loop Skill`, `$chain-loop-skill`, and Level terminology.

## License

MIT.
