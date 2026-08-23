# CLK 3.0.2 Loop Engineering Identity Design

## 1. Problem

CLK 3.0.1 correctly reuses SLK for Chain construction, but its opening definition can still be read as a parallel workflow that merely borrows SLK procedures. That understates the actual method identity and leaves the same risk of confusing conversation activation with engineering progress.

CLK is a Loop Engineering form built from SLK Loops.

## 2. Canonical identity

CLK is the composite parallel-and-fusion form of Loop Engineering for a medium or large engineering Run.

One CLK owns one Run. It begins with two or more independent foreground Chains. Every foreground Chain is formally one complete SLK Loop. After the necessary foreground Chain results have passed their Chain D2 and been frozen, one Fusion Chain runs as another SLK Loop and integrates them into the Run result.

```text
CLK plan + complete fusion contracts
        ↓
SLK Loop A ─┐
SLK Loop B ─┼─ concurrent independent construction → frozen Chain results
SLK Loop C ─┘
        ↓
Fusion Chain = SLK Loop with one or more GO
        ↓
final D2 → CLK Run result
```

This is a nested Loop topology, not a set of unrelated tasks followed by a one-time file merge.

## 3. SLK is the execution Loop

Each foreground Chain and the Fusion Chain uses the complete SLK Loop:

```text
CELL dispatch → Worker construction + D0 → candidate → isolated D1
       ↑                                                ↓
       └──────────── focused rework on D1 FAIL ─────────┘
                       D1 PASS → next CELL
```

CLK does not redefine Worker, Checker, D0, D1, rework, communication recovery, or model selection. Those remain SLK responsibilities.

CLK adds only the upper-level concerns that make several SLK Loops compose:

- Chain partition and ownership;
- complete fusion interface contracts;
- temporary parallel isolation and shared-resource coordination;
- concurrent Chain launch;
- shared-Supervisor Chain D2 boundaries;
- frozen result collection and Fusion Chain launch;
- final D2 and CLK Run closure.

## 4. Roles and communication

CLK adds no new role. One shared Supervisor coordinates the Run; each active Chain has its own Checker and Worker as defined by SLK.

Conversation activation transports assignments and results between Loop nodes. It does not define progress. A receipt does not complete the recipient's assigned node, and ending a member's completed activity does not stop the enclosing SLK or CLK Loop. Members do not watch peer construction state or use `wait_threads` as an orchestration engine.

## 5. Change boundary

The 3.0.2 patch will:

1. identify CLK as the composite Loop Engineering form built from SLK Loops;
2. formally name every foreground Chain and Fusion Chain as an SLK Loop;
3. separate Loop progress from conversation activation;
4. update only directly affected CLK Skills and semantic tests;
5. preserve Chain planning, fusion contracts, parallel isolation, shared Supervisor, role count, record layout, and child-Skill set;
6. preserve or reduce existing Skill line counts.

The patch will not restore Stages, Patrol, Verification roles, online watching, hard barriers unrelated to the current 3.0 design, or an independent CLK CELL protocol.

## 6. Verification

Repository tests will mechanically prove that:

- CLK identifies itself as a composite Loop Engineering form;
- every foreground Chain and Fusion Chain is an SLK Loop;
- CLK reuses rather than duplicates the SLK execution Loop;
- conversation activation is not treated as engineering progress;
- members do not watch peers or use `wait_threads` as the Loop;
- all 3.0 roles and integration responsibilities remain unchanged;
- Skill line counts do not grow.
