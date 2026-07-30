# Topology Fault Localization

## Boundary

This capability diagnoses failures only inside one frozen CLK topology: persistent
Chains, ordered Levels, and full Barriers. It does not define products, create a
debugging role, add a verification layer, run an SLK micro-loop, or activate a GLK
dependency graph.

Diagnosis is evidence gathering, not acceptance. D0, D1, D2, conditional LEVEL,
D3, and Barrier Receipts retain their existing authorities.

## Required record

Before product rework, freeze one append-only `TOPOLOGY_FAULT_RECORD` binding:

- Run, Baseline, Level, and affected Chain identities;
- immutable candidate and attempt references plus Receipt and evidence hashes;
- exactly one fault class and one hypothesis;
- any comparable healthy-Chain control;
- Receipt catalog, consumption edges, identity changes, exact invalidation set,
  preserved Receipts, and reverification scopes;
- route, escalation trigger, issuer, and time.

The mutable runtime index contains only references to unresolved records. History
remains append-only.

## Fault classes

| Class | Evidence boundary | Native route |
|---|---|---|
| `CHAIN_LOCAL` | One Chain candidate or its D0/D1/D2 contract | Existing Checker/Worker rework |
| `CROSS_CHAIN_COMPOSITION` | Frozen GO outputs pass individually but a new LEVEL claim fails | Fresh LEVEL evidence or `PLAN_DEFECT` |
| `LEVEL_BARRIER` | Candidate set, terminal-state map, amendment binding, or atomic transition is inconsistent | Barrier recalculation or `PLAN_DEFECT` |

Do not classify by convenience. If evidence changes the product definition, route
`CALABASH_REVIEW_REQUIRED`. If a solution needs partial unlock, a new Chain, a
cycle, conditional routing, or runtime path choice, route
`METHOD_BOUNDARY_EXCEEDED` to GLK.

## One-hypothesis rule

One fault series has at most one `ACTIVE` hypothesis. The record states a predicted
observation and a falsifier before mutation. A falsified hypothesis becomes an
immutable `FALSIFIED` record. Its successor uses a new record and reciprocal
`supersedes` / `superseded_by` links.

Never stack another speculative patch on the same active hypothesis. A diagnostic
probe may add evidence but cannot issue a product verdict.

## Healthy same-Level controls

A healthy Chain is a control only when a frozen input, interface, or environment
basis proves comparability. Record that basis and its D2 Receipt identity.

The control remains read-only evidence. Its D2 cannot substitute for the affected
Chain, cannot be invalidated merely for comparison, and cannot become a same-Level
input or dependency.

## Minimum closure

Compute closure from declared Receipt consumption edges:

1. Seed the set with Receipts invalidated by changed identities.
2. Add only Receipts that directly or transitively consume an invalidated Receipt.
3. Preserve every catalogued Receipt outside that transitive set.
4. Reverify exactly the layer and scope of each invalidated Receipt.

When D2 candidates are unchanged and the fault is cross-Chain composition, gather
only fresh LEVEL evidence. For a pure `LEVEL_BARRIER` correction, change no product
identity, invalidate no technical Receipt, preserve the full catalog, and
recalculate only the Barrier.

An unresolved record referencing the current Level blocks Barrier PASS. Other
same-Level Chains may continue only while evidence proves the fault cannot
invalidate their candidates or independence.

## Stop and hand off

Stop local rework and route `PLAN_DEFECT` when the proposed correction changes GO
outcome, scope, acceptance, ownership, dependencies, Chain membership, Level
membership, or the Barrier claim. Use a versioned CLK amendment only when fixed
Chains, ordered Levels, full Barriers, and no same-Level dependency remain valid.

CLK may hand LCCoding a frozen fault package, but it does not own project lifecycle,
security closure, or Delivery. Calabash owns product-definition review. A future
strict one-line Run may select SLK at a method boundary; the active CLK Run never
loads it. Dynamic dependency activation belongs to GLK.
