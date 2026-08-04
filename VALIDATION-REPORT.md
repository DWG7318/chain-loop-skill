# CLK 2.5.0 Validation Report

## Candidate

- Product: Chain Loop Skill (CLK)
- Version: 2.5.0
- Branch: `feature/clk-2.5.0-worker-wake-patrol`
- Repository database ID: `1298120736`
- Local validation date: 2026-08-04
- Local platform: Windows, Python 3.14
- CI target: Ubuntu, Python 3.11

## Local release-gate result

PASS. The following commands completed with exit code 0 on the candidate:

```text
python scripts/validate_repository.py
PASS: CLK repository 2.5.0

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

python scripts/validate_receipt_chain.py chain-loop-skill/templates/d0-worker-receipt.yaml chain-loop-skill/templates/d1-checker-receipt.yaml chain-loop-skill/templates/d2-go-verification-receipt.yaml
PASS: CLK Receipt chain

python -m pytest -q
176 passed, 181 subtests passed

python -O -m pytest tests/test_run_control.py::test_critical_invalid_traces_fail_closed_in_normal_and_optimized_modes tests/test_topology_faults.py::test_cross_field_invalid_records_fail_with_and_without_assertions -q
20 passed; the expected pytest optimized-mode warning was emitted

git diff --check
PASS
```

## Run-control acceptance evidence

The candidate proves:

- Worker-only T+0/T+2/T+4/T+6 wake escalation, exact frozen Checker identity,
  archive/host repair without guessing, ACK stop, temporary-heartbeat cleanup, and
  deterministic `PENDING_WAKE` fallback;
- Supervisor no-wait behavior and exactly one visible Luna+xhigh mechanical Run
  patrol/heartbeat, including pause tolerance, duplicate rejection, pending-wake
  consumption, and terminal cleanup/archive;
- visible peer tasks are not subagents, while spawned/delegated/hidden/background
  Agent evidence is rejected;
- delivery does not increment acceptance, D1 PASS increments once, duplicate or
  rework receipts do not, GO candidate readiness differs from D2, and amendments
  version/recompute denominators without rewriting history;
- unknown or insufficient device capacity blocks or splits before dispatch; actual
  load feedback tightens later gates; Worker self-split is rejected; post-dispatch
  splits of 3, 6, 7, or 8 successors are severe and re-evaluate remaining work;
- every method role denies Pin capability; explicit Owner Pin is accepted, Agent
  Pin is `UNAUTHORIZED_THREAD_PIN`, unknown provenance is
  `PIN_PROVENANCE_UNKNOWN`, and Pin-then-Unpin preserves violation evidence without
  automatic unpin.

Existing topology, Receipt, Barrier, identity, authority, repository-drift,
malformed-structure, and hash-mismatch negative gates remain passing.

## Integrity and boundary

`FILE_HASHES.json` covers every release file except itself using LF-normalized
SHA-256 for text and byte hashes for binary files. Local evidence does not claim
GitHub or release state. Push, merge, PR, tag, and Release remain unperformed and
require separate authorization and remote validation of the exact commit.
