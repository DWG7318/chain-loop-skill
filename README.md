# Chain Loop Skill (CLK)

Current version: **3.0.1**

CLK organizes one medium or large engineering Run as:

```text
2+ concurrent SLK construction Chains -> 1 Fusion SLK Chain
```

Each construction Chain has a linear GO/CELL path and its own Checker/Worker pair. All pairs share one Supervisor, start in the same construction cycle, and work in temporary physical isolation while following complete fusion interface contracts. After every required construction Chain passes D2, one Fusion Chain combines the frozen results into the final system.

## Roles and method boundary

- The Owner confirms every new CLK Run before its Supervisor is created.
- The originating conversation plans the Run, hands it to a new Supervisor, and then exits engineering work.
- The shared Supervisor understands CLK and SLK, coordinates the Chains, performs each Chain D2, and starts and closes Fusion.
- Each Checker and Worker follows SLK. CLK does not add role types or replace SLK's D0/D1/D2, rework, communication, records, or model guidance.

CLK is project-level orchestration; SLK remains the execution method inside every construction Chain and the Fusion Chain.

## Core flow

1. Finalize the current Run, 2+ independent Chains, their linear GO/CELL plans, complete fusion interface contracts, and temporary isolation.
2. Obtain Owner confirmation and create a new shared Supervisor.
3. The Supervisor demonstrates SLK understanding, then CLK-specific understanding.
4. Create every visible Checker/Worker pair and test Supervisor ↔ Checker, Checker ↔ Worker, and the emergency Supervisor ↔ Worker route.
5. Start all construction Chains together.
6. Perform an isolated D2 for each Chain. A failed Chain returns only to its own Checker/Worker loop; other independent Chains continue.
7. Freeze every passed handoff, then plan and start one Fusion SLK Chain with one or more linear GOs.
8. Use the Fusion D2 as the final CLK Run D2, archive the completed member conversations, and send the Owner one concise conclusion.

## Skill collection

CLK 3.0.1 is distributed as 9 sibling Skill directories:

| Skill | Purpose |
| --- | --- |
| `skills/chain-loop-skill/SKILL.md` | Main router and method identity |
| `skills/clk-plan-run/SKILL.md` | Run, Chain, GO/CELL, Owner confirmation, and handoff planning |
| `skills/clk-design-fusion-contracts/SKILL.md` | Complete fusion interface contracts and executable checks |
| `skills/clk-plan-parallel-isolation/SKILL.md` | Temporary physical isolation without contract drift |
| `skills/clk-grill-supervisor/SKILL.md` | SLK-first, CLK-second Supervisor understanding |
| `skills/clk-launch-chains/SKILL.md` | Visible members, communication tests, and synchronous launch |
| `skills/clk-complete-chain/SKILL.md` | Isolated Chain D2, frozen handoff, and member archive |
| `skills/clk-start-fusion/SKILL.md` | Fusion planning, new worktree, and Fusion pair startup |
| `skills/clk-close-run/SKILL.md` | Final Fusion D2, record, archive, and Owner conclusion |

Install or copy the 9 directories together so the main Skill can route to its children. SLK is a separate dependency and is entered through `$small-loop-skill`.

## Records

- CLK summary: `CLK-RUN-<RUN-ID>-RECORD.md`
- Construction Chain: `SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md`
- Fusion Chain: `SLK-RUN-<RUN-ID>-FUSION.md`

Each role records its own work facts. The CLK root record summarizes identities, states, evidence paths, errors, rework, exemptions, frozen handoffs, archive state, and the final conclusion without copying full member logs.

## Validation

```powershell
python scripts/validate_repository.py
python scripts/quick_validate.py skills
python -m pytest -q
```

See [README.zh-CN.md](README.zh-CN.md), [MIGRATION.md](MIGRATION.md), and [VALIDATION-REPORT.md](VALIDATION-REPORT.md).
