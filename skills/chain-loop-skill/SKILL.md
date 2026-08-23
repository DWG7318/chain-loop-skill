---
name: chain-loop-skill
description: Use when a medium or large engineering Run has two or more independent construction streams that can progress concurrently before final integration.
---

# Chain Loop Skill

## 方法身份

CLK 是建立在 SLK Loop 之上的 Loop Engineering 的复合形态，面向中型或大型工程。一个 CLK 对应一个 Run：项目层使用 CLK，Chain 施工使用 SLK。

CLK 把工作分成两条或以上前置 Chain，每条前置 Chain 都是一个完整的 SLK Loop，有线性 GO 与 CELL、独立 Checker 和独立 Worker；所有前置 Chain 在同一施工周期同时推进，并共享一个 Supervisor，各自完成 Worker D0、Checker D1 和共享 Supervisor D2。

全部必要 Chain 通过 D2 后建立一条 Fusion Chain；Fusion Chain 也是一个完整的 SLK Loop，可以包含一个或多个 GO 并线性推进，它的 D2 是整个 CLK Run 的最终 D2。

## 使用关系

原对话与 Owner 正式确定当前 Run 的 Chain、GO、初始 CELL、融合合同、临时并行隔离和 Fusion 轮廓。Owner 确认本 Run 后，原对话创建新的 Supervisor并完成双向通讯测试，再退出工程工作。

Supervisor 先读取 CLK；CLK 再进入 `$small-loop-skill`，让 Supervisor 充分理解 SLK，随后回到 CLK 理解多 Chain 编排。Checker 和 Worker 只使用 SLK，不读取 CLK。

每个新 CLK Run 使用新的 Supervisor。未来 Run 可以预规划，但会在上一 Run 交付后依据真实基线正式定稿，并再次取得 Owner 确认。

Supervisor 在项目根目录创建和修改结构权威 `CLK-CHAIN-MAP.md`，所有成员可以读取；`CLK-RUN-<RUN-ID>-RECORD.md`只保存Run历史、证据链接、决定和结论。每条前置 Chain 使用 `SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md`，Fusion 使用 `SLK-RUN-<RUN-ID>-FUSION.md`，不复制成员详细记录。

## 按当前情境选择指导

- 建立当前 Run、划分 Chain 和准备 Owner 确认：`$clk-plan-run`
- 设计完整融合接口与可执行合同检查：`$clk-design-fusion-contracts`
- 设计临时并行工作空间与资源边界：`$clk-plan-parallel-isolation`
- Supervisor 完成 SLK 与 CLK 两段理解确认：`$clk-grill-supervisor`
- 建立全部成员、测试通讯并同时开工：`$clk-launch-chains`
- 对一条前置 Chain 执行 D2、冻结成果并归档：`$clk-complete-chain`
- 根据已冻结的真实输入启动 Fusion Chain：`$clk-start-fusion`
- 完成最终 D2、记录、归档和 Owner 结论：`$clk-close-run`

日常 CELL 施工、D0、D1、返工、通讯恢复、模型选择和成员恢复继续由 SLK 对应情境指导；消息只传输 Loop 工作和结果，成员完成当前 Loop 节点和必要交接后结束当前活动，接收回执不代表节点完成。成员不使用`wait_threads`或读取其他成员施工状态，下一条真实消息重新激活；CLK 不重复定义。
