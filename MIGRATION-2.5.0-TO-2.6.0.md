# Migration: CLK 2.5.0 to 2.6.0

## Scope

CLK 2.6.0 changes model selection and binding evidence only. Fixed persistent
Chains, ordered Levels, full Barriers, D0–D3, Worker wake, layered progress, CELL
capacity, patrol authority, and task-Pin policy remain unchanged.

## Required changes

1. Create one versioned `MODEL_BINDING_LEDGER` for the Run and bind every required
   technical actor plus the separate unique patrol.
2. Replace the former fixed patrol Luna binding with the default
   `gpt-5.6-terra+xhigh` binding. Patrol remains nontechnical and non-authoritative.
3. Default ordinary technical work to `gpt-5.6-terra+xhigh`.
4. Permit `gpt-5.6-luna+xhigh` only for a Worker whose current CELL Contract is
   explicitly fine-grained, LOW-risk, and capacity-PASS.
5. Permit `gpt-5.6-sol+xhigh` only for evidenced high-complexity correction,
   root-cause diagnosis, or complex rework.
6. For another provider/model, add a content-hashed `PROVEN_EQUIVALENT` record for
   the exact selected tier and capability class.
7. Remove all active GPT 5.5-or-lower bindings. They cannot be grandfathered.
8. Keep `xhigh` unless the Owner explicitly authorizes `ultra` for the exact current
   Run, actor, binding, and scope.
9. When model or effort changes, close the old binding, create a new binding and
   reciprocal change record, and repeat readiness, isolation, and verification.

## Fail-closed states

- Missing or non-PASS equivalence evidence.
- Luna outside an eligible Worker CELL.
- Sol for ordinary implementation or checking.
- GPT 5.5 or lower.
- `ultra` without exact Owner evidence.
- An actor/scope observed under a different model or effort with the same binding.
- Reused conversation, context, workspace, runtime namespace, evidence path, or
  readiness/isolation/verification Receipt across role bindings.

## Validation

```text
python scripts/validate_model_policy.py chain-loop-skill/templates/model-binding-ledger.yaml
python -O scripts/validate_model_policy.py chain-loop-skill/templates/model-binding-ledger.yaml
python scripts/validate_run_control.py chain-loop-skill/templates/run-control-trace.yaml
python scripts/validate_repository.py
python -m pytest -q
```
