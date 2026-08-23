# Chain Loop Skill（CLK）

当前版本：**3.0.1**

CLK面向中型或大型工程，把一个Run组织为：

```text
两条或以上并行的 SLK 施工 Chain -> 一条 Fusion SLK Chain
```

每条施工Chain都有线性的GO/CELL、独立Checker和独立Worker；所有成员组共享一个Supervisor，在同一施工周期启动。并行施工使用临时物理隔离，同时遵守完整融合接口合同。所有必需施工Chain通过D2并冻结交接后，由一条Fusion Chain把真实成果接成完整系统。

## 角色与方法边界

- 每个新CLK Run开工前都由Owner确认。
- 原对话负责策划Run、创建新Supervisor并完成交接，随后退出具体工程工作。
- 共享Supervisor理解CLK与SLK，协调各Chain，完成各Chain D2，并负责启动和收口Fusion。
- Checker与Worker只按SLK施工。CLK不增加新角色，也不重复定义SLK的D0/D1/D2、返工、通讯、记录和模型指导。

CLK负责项目层编排；每条施工Chain和Fusion Chain内部都由SLK负责。

## 核心流程

1. 定稿当前Run、两条或以上独立Chain、线性GO/CELL计划、完整融合接口合同和临时隔离。
2. 取得Owner确认并创建新的共享Supervisor。
3. Supervisor先证明理解SLK，再证明理解本次CLK编排。
4. 创建全部可见Checker/Worker成员组，测试Supervisor ↔ Checker、Checker ↔ Worker和应急Supervisor ↔ Worker路线。
5. 所有施工Chain在同一施工周期一起开工。
6. 每条Chain单独接受隔离D2。失败只回到所属Checker/Worker返工，其他独立Chain继续。
7. 冻结全部通过的交接，再规划并启动一条可以包含多个线性GO的Fusion SLK Chain。
8. Fusion D2直接作为CLK Run最终D2；归档成员对话，并向Owner发送一个简洁结论。

## Skill集合

CLK 3.0.1由9个并列Skill目录组成：

| Skill | 用途 |
| --- | --- |
| `skills/chain-loop-skill/SKILL.md` | 主入口、方法身份与情境路由 |
| `skills/clk-plan-run/SKILL.md` | Run、Chain、GO/CELL、Owner确认与交接规划 |
| `skills/clk-design-fusion-contracts/SKILL.md` | 完整融合接口合同与可执行检查 |
| `skills/clk-plan-parallel-isolation/SKILL.md` | 不改变合同的临时物理隔离 |
| `skills/clk-grill-supervisor/SKILL.md` | 先SLK、后CLK的Supervisor理解确认 |
| `skills/clk-launch-chains/SKILL.md` | 可见成员、通讯测试与同步开工 |
| `skills/clk-complete-chain/SKILL.md` | 隔离Chain D2、冻结交接与成员归档 |
| `skills/clk-start-fusion/SKILL.md` | Fusion规划、新worktree与成员组启动 |
| `skills/clk-close-run/SKILL.md` | 最终D2、记录、归档与Owner结论 |

安装或复制时请让9个目录保持并列，使主Skill能够路由到各子Skill。SLK是单独依赖，通过`$small-loop-skill`进入。

## 记录

- CLK汇总：`CLK-RUN-<RUN-ID>-RECORD.md`
- 施工Chain：`SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md`
- Fusion Chain：`SLK-RUN-<RUN-ID>-FUSION.md`

各角色记录自己的工作事实；CLK根记录只汇总身份、状态、证据路径、错误、返工、豁免、冻结交接、归档状态和最终结论，不复制成员全文。

## 验证

```powershell
python scripts/validate_repository.py
python scripts/quick_validate.py skills
python -m pytest -q
```

版本边界见[MIGRATION.md](MIGRATION.md)，当前验证证据见[VALIDATION-REPORT.md](VALIDATION-REPORT.md)。
