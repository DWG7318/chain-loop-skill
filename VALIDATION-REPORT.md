# CLK 2.3.1 Validation Report

## Candidate

- Product: Chain Loop Skill (CLK)
- Version: 2.3.1
- Branch: `agent/clk-2.3.1`
- Repository database ID: `1298120736`
- Local validation date: 2026-07-29
- Local platform: Windows, Python 3.14
- CI target: Ubuntu, Python 3.11

## Local release-gate result

PASS. The following commands completed with exit code 0 on the candidate:

```text
python scripts/validate_repository.py
PASS: CLK repository 2.3.1

python scripts/validate_chain_level_plan.py tests/fixtures/plans/valid-minimal.yaml
PASS: Chain/Level plan

python scripts/validate_runtime_state.py tests/fixtures/runtime/valid-level-active.yaml
PASS: CLK runtime state

python scripts/validate_receipt_chain.py chain-loop-skill/templates/d0-worker-receipt.yaml chain-loop-skill/templates/d1-checker-receipt.yaml chain-loop-skill/templates/d2-go-verification-receipt.yaml
PASS: CLK Receipt chain

python -m pytest -q
71 passed, 180 subtests passed
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
- consumed Receipt hash mismatch;
- immutable candidate mismatch between consumed Receipts;
- missing Skill frontmatter;
- repository version drift;
- release-file hash mismatch;
- malformed YAML.
- pip cache configured without the declared dependency-file path.

## Integrity

`FILE_HASHES.json` is generated from every release file except itself. Repository
validation requires exact coverage and verifies every SHA-256 digest. The hash map
is an integrity record for the candidate; repository identity and the signed Git
history/tag provide provenance.

## CI boundary

This report records local candidate evidence. GitHub Actions evidence is produced
separately by `.github/workflows/validate.yml` after push. Merge and `v2.3.1` tag
creation remain blocked unless the remote workflow passes on the exact commit.
