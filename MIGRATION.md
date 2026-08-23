# CLK 2.6.0 to 3.0.0

## 3.0.3 clarification

New Runs create `CLK-CHAIN-MAP.md` as the sole Supervisor-owned Chain/Fusion structure authority, bind one latest-SLK baseline, use `$slk-select-models` for every role choice, and leave cross-Chain code integration to Fusion's independent worktree. Existing 3.0.0-3.0.2 records remain history and are not rewritten.

CLK 3.0.0 is a method reconstruction, not an incremental expansion of the 2.6.0 control kernel.

## Architecture boundary

Version 2.6.0 modeled persistent Chains, synchronized Levels, additional verification machinery, runtime state, patrol, receipts, model ledgers, and fixed control contracts inside CLK.

Version 3.0.0 keeps only CLK's distinct project-level value:

```text
2+ concurrent SLK construction Chains -> 1 Fusion SLK Chain
```

It reuses SLK for every linear Chain, including roles, D0/D1/D2, CELL execution, rework, communication, records, recovery, and model selection. CLK adds only concurrent Chain planning, complete fusion contracts, temporary isolation, shared-Supervisor coordination, Chain D2 handoffs, and one final Fusion Chain.

## Active method

3.0.0不保留第二套活跃内核。旧2.6.0文件和术语只作为Git历史理解来源，不作为新Run的并行运行规则。新CLK Run从`skills/chain-loop-skill/SKILL.md`进入，并让主Skill按情境路由到8个子Skill。

The migration does not reinterpret an already running 2.6.0 project in place. Establish a new 3.0.0 Run from the project's real current baseline, confirm it with the Owner, and create a new Supervisor.

## Record mapping

- Replace the old runtime/Level control record with `CLK-RUN-<RUN-ID>-RECORD.md`.
- Give every construction Chain its own `SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md`.
- Give Fusion its own `SLK-RUN-<RUN-ID>-FUSION.md`.
- Preserve useful historical evidence by reference; do not copy old control state into current authority fields.
