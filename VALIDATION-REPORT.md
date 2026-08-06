# CLK 2.6.0 Validation Report

## Candidate

- Product: Chain Loop Skill (CLK)
- Version: 2.6.0
- Branch: `feature/clk-2.6.0-controllable-model-policy`
- Repository database ID: `1298120736`
- Local validation date: 2026-08-06
- Local platform: Windows, Python 3.14
- CI target: Ubuntu, Python 3.11

## Local candidate-gate result

PASS. Fresh local output on the candidate:

```text
python -m pytest -q
247 passed, 185 subtests passed

python -O -m pytest -q \
  tests/test_model_policy.py::test_known_gpt_family_laundering_fails_under_python_optimized \
  tests/test_model_policy.py::test_critical_invalid_policy_fails_closed_under_python_optimized \
  tests/test_run_control.py::test_critical_invalid_traces_fail_closed_in_normal_and_optimized_modes \
  tests/test_topology_faults.py::test_cross_field_invalid_records_fail_with_and_without_assertions
40 passed; one expected pytest optimized-mode warning

python scripts/validate_repository.py
PASS: CLK repository 2.6.0

python scripts/validate_chain_level_plan.py tests/fixtures/plans/valid-minimal.yaml
PASS: Chain/Level plan

python scripts/validate_runtime_state.py tests/fixtures/runtime/valid-level-active.yaml
PASS: CLK runtime state

python scripts/validate_topology_fault.py tests/fixtures/topology-faults/valid-chain-local.yaml
python scripts/validate_topology_fault.py tests/fixtures/topology-faults/valid-cross-chain.yaml
python scripts/validate_topology_fault.py tests/fixtures/topology-faults/valid-level-barrier.yaml
PASS: CLK topology fault record (each fixture)

python scripts/validate_run_control.py chain-loop-skill/templates/run-control-trace.yaml
PASS: CLK run control trace

python scripts/validate_model_policy.py chain-loop-skill/templates/model-binding-ledger.yaml
PASS: CLK model binding policy

python scripts/validate_receipt_chain.py \
  chain-loop-skill/templates/d0-worker-receipt.yaml \
  chain-loop-skill/templates/d1-checker-receipt.yaml \
  chain-loop-skill/templates/d2-go-verification-receipt.yaml
PASS: CLK Receipt chain

git diff --check
PASS
```

## Model-policy acceptance evidence

The candidate proves:

- `MODEL_BINDING_LEDGER` binds the Run roster, current CELL contracts, capability
  class/equivalence, actual model, provider, reasoning effort, selection tier and
  reason, exact scope, isolation identities, content-hashed evidence, and fresh
  readiness/isolation/verification Receipts;
- the Run ledger covers at least two Checker/Worker Chains and their current
  Verification bindings, while patrol remains one separate nontechnical actor;
- canonical technical roles and patrol default to `gpt-5.6-terra+xhigh`;
- `gpt-5.6-luna+xhigh` passes only for a Worker whose current CELL is explicitly
  fine-grained, LOW-risk, and capacity-PASS;
- `gpt-5.6-sol+xhigh` passes only for evidenced high-complexity correction,
  root-cause diagnosis, or complex rework;
- another model passes only through content-hashed `PROVEN_EQUIVALENT` evidence
  that exactly matches its actual model, selected tier, and capability class;
- GPT IDs require canonical lowercase and no outer whitespace; boundary-safe
  Terra/Luna/Sol family parsing recognizes hyphen snapshots without confusing
  `lunar` with `luna`, and a known family can never cross tiers through equivalence;
- GPT 5.5 and lower, unapproved `ultra`, cost/convenience downgrade, Luna outside
  an eligible Worker CELL, ordinary Sol, unproven/unknown equivalence, named
  reference-model tier laundering, and patrol Luna bypass fail closed;
- item-specific Owner evidence may authorize `ultra` only for the exact current
  Run, actor, binding, and scope;
- a legitimate actual-model or reasoning-effort change closes the prior binding, creates a reciprocal
  `MODEL_BINDING_CHANGE`, and supplies a new isolated binding with fresh readiness,
  isolation, verification, selection, and observation evidence;
- an exact Owner-authorized Terra `xhigh`→Terra `ultra` rebind passes, while an
  unauthorized effort change, a full no-op change, and old-binding effort drift fail;
- missing switch records, reused gate Receipts, actual-model/reasoning observation
  drift, duplicate active bindings, single-Chain Run fragments, role pollution,
  patrol CELL scope, and same-model capability/isolation reuse fail closed in normal
  and optimized Python.

## Preserved 2.5.0 behavior

All prior topology and runtime suites remain green. The candidate does not change:

- fixed persistent Chains, maximum valid Chain count, ordered Levels, or full
  Barriers;
- D0/D1/D2/conditional LEVEL/D3 authority and Receipt consumption;
- topology fault localization, identity, issuer, closure, or route semantics;
- Worker-only wake escalation, Supervisor no-wait rule, layered progress,
  device/cumulative-load CELL capacity, Pin policy, or patrol authority;
- the boundary to LCCoding, Calabash, SLK, or GLK.

The former fixed patrol Luna value is replaced only at the model-binding interface:
patrol now follows the Owner-controllable Terra default and remains non-authoritative.

## Integrity and boundary

`FILE_HASHES.json` covers every release file except itself using LF-normalized
SHA-256 for text and byte hashes for binary files. Active compatibility guidance
contains no GPT 5.5-or-lower positive authorization; remaining 5.5 occurrences are
rejection examples or negative tests. No secret, foreign-role, or cross-method
implementation surface was added. Local evidence makes no remote-state claim.

Per Owner instruction, push, merge, PR, tag, Release, and publication were not
performed for this candidate.
