# LCCoding Interface

## Input

LCCoding provides a frozen Run Contract with Feature Slice and Calabash Baseline
references, Run Feature, scope, acceptance and evidence claims, autonomy envelope,
safety boundary, and immutable candidate policy.

## Output

CLK returns the final Run candidate, Chain/Level Baseline, D0-D3 and conditional
Level Receipts, Barrier Receipts, Owner Acceptance guide and verdict, and a final
evidence index.

`LOOP_OWNER_ACCEPTED` means only that the bounded Run product was accepted. CLK sets
`project_security_closed: false` and `delivery_authorized: false`.

## Outer gates

After all required Runs are accepted, LCCoding invokes an independent centralized
Security Auditor, routes findings to engineering roles, requires auditor
reverification, conducts Post-Security Owner Acceptance, and governs Delivery.
