# CLK Model Selection and Binding

## Purpose

CLK 2.6.0 selects capability from current work facts instead of permanently fixing
one model to a role. `MODEL_BINDING_LEDGER` is the sole machine-checkable authority.
It records the selected tier, actual model, reasoning effort, reason, capability
class, equivalence evidence, isolation identity, and verification receipts.

This policy does not change fixed Chains, ordered Levels, full Barriers, D0–D3, or
role authority.

## Selection table

| Work facts | Role | Reference binding | Required reason |
|---|---|---|---|
| Ordinary technical work | Any technical role | `gpt-5.6-terra+xhigh` | `DEFAULT_TECHNICAL` |
| Ordinary patrol work | Unique Run patrol | `gpt-5.6-terra+xhigh` | `DEFAULT_PATROL` |
| Fine-grained, LOW-risk, capacity-PASS CELL | Worker only | `gpt-5.6-luna+xhigh` | `FINE_GRAINED_LOW_RISK_CELL` |
| High-complexity correction | Technical role | `gpt-5.6-sol+xhigh` | `HIGH_COMPLEXITY_CORRECTION` |
| Root-cause diagnosis | Technical role | `gpt-5.6-sol+xhigh` | `ROOT_CAUSE_DIAGNOSIS` |
| Complex rework | Technical role | `gpt-5.6-sol+xhigh` | `COMPLEX_REWORK` |

Cost, convenience, queue pressure, and role title are not selection evidence.
Ordinary implementation and ordinary checking stay on Terra. Luna eligibility is
read from the current versioned CELL contract; delivery text cannot self-certify it.

## Capability-equivalent alternatives

The GPT names above are reference bindings. Another model may replace one only when
a content-hashed `CAPABILITY_EQUIVALENCE` record states:

```text
actual_model
target_selection_tier
capability_class
result = PROVEN_EQUIVALENT
evidence.path + evidence.sha256
```

`UNKNOWN`, `NOT_EQUIVALENT`, a different tier, a different model, missing evidence,
or a free-text claim fails closed. GPT 5.5 and lower are prohibited regardless of
claimed equivalence.

## Reasoning effort

`xhigh` is the normal binding. `ultra` requires one Owner authorization that binds
the current Run, actor, binding ID, exact GO/CELL/Round scope, and content-hashed
evidence. Old, generic, inferred, or cross-scope authorization is invalid.

## Binding and isolation

Every required actor has exactly one current `ACTIVE` binding. Patrol is included
in this ledger only to enforce the same binding discipline; it remains a separate,
non-authoritative, nontechnical role and never enters the canonical technical-role
enum or a D layer.

Because the ledger is Run-scoped, its roster covers at least two paired
Checker/Worker Chains and their current Verification bindings; a one-Chain fragment
cannot masquerade as the Run ledger.

Same-model use is legal only with distinct conversation, context, workspace,
runtime namespace, binding, and evidence identities. Readiness, isolation, and
binding verification must all be fresh `PASS` Receipts.

## Model changes

Never edit the actual model inside an active binding. A legitimate change creates a
new binding and `MODEL_BINDING_CHANGE`, reciprocally links `supersedes` and
`superseded_by`, closes the old binding, and supplies new reason, selection evidence,
readiness, isolation, and verification Receipts. Observed model or reasoning drift
under the old binding is `SILENT_MODEL_SWITCH` and fails closed.

Round advancement, rework, wake escalation, progress updates, or patrol activity do
not themselves authorize a model change.

## Mechanical validation

Run:

```text
python scripts/validate_model_policy.py chain-loop-skill/templates/model-binding-ledger.yaml
```

The validator uses explicit checks and has the same fail-closed behavior under
`python -O`.
