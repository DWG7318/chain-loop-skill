# CLK 2.4.0 Validation Report

## Candidate

- Product: Chain Loop Skill (CLK)
- Version: 2.4.0
- Branch: `feature/clk-2.4.0`
- Repository database ID: `1298120736`
- Local validation date: 2026-07-30
- Local platform: Windows, Python 3.14
- CI target: Ubuntu, Python 3.11

## Local release-gate result

PASS. The following commands completed with exit code 0 on the candidate:

```text
python scripts/validate_repository.py
PASS: CLK repository 2.4.0

python scripts/validate_chain_level_plan.py tests/fixtures/plans/valid-minimal.yaml
PASS: Chain/Level plan

python scripts/validate_runtime_state.py tests/fixtures/runtime/valid-level-active.yaml
PASS: CLK runtime state

python scripts/validate_topology_fault.py tests/fixtures/topology-faults/valid-chain-local.yaml
PASS: CLK topology fault record

python scripts/validate_receipt_chain.py chain-loop-skill/templates/d0-worker-receipt.yaml chain-loop-skill/templates/d1-checker-receipt.yaml chain-loop-skill/templates/d2-go-verification-receipt.yaml
PASS: CLK Receipt chain

python -m pytest -q
88 passed, 208 subtests passed
```

## Negative evidence

The candidate rejects all dedicated invalid fixtures and mutations:

- one-Chain CLK plan;
- duplicate GO ownership across Chains;
- Chain GO order reversal;
- duplicate Level ordinal;
- two open Levels;
- two ACTIVE GOs in one Chain;
- unresolved Optional GO at Barrier;
- formal resolution used instead of Required D2 PASS;
- incomplete Required/Optional assignment coverage in a Barrier Receipt;
- reused Verification attempt/context/workspace/evidence identity;
- topology fault class outside the three-value CLK enum;
- more than one active hypothesis in one fault series;
- unproven healthy-Chain comparability or D2 substitution/dependency;
- non-minimal Receipt-consumption invalidation/reverification closure;
- product Receipt invalidation during a Barrier-only correction;
- unresolved current-Level topology fault at Barrier PASS;
- consumed Receipt hash mismatch;
- immutable candidate mismatch between consumed Receipts;
- missing Skill frontmatter;
- repository version drift;
- release-file hash mismatch;
- malformed YAML.
- pip cache configured without the declared dependency-file path.

## Integrity

`FILE_HASHES.json` is generated from every release file except itself. Repository
validation requires exact coverage and verifies every SHA-256 digest. Text content
is normalized to canonical LF before hashing so Windows and Linux checkouts produce
the same digest; binary content is hashed byte-for-byte. The hash map is an
integrity record for the candidate; repository identity and the signed Git
history/tag provide provenance.

## CI boundary

This report records local candidate evidence. GitHub Actions evidence is produced
separately by `.github/workflows/validate.yml` after push. Merge and `v2.4.0` tag
creation remain blocked unless the remote workflow passes on the exact commit.
