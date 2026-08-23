---
name: clk-start-fusion
description: Use when all required construction Chains in an active Chain Loop Skill (CLK) Run have frozen D2-passed handoffs and the shared Supervisor is ready to form the Fusion execution stream.
---

# Start the Fusion Chain

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

用所有必需施工Chain的D2 PASS冻结交接定稿融合施工，并建立一条Fusion Chain把真实成果接成完整系统。

## 定稿融合施工

1. Supervisor核对每条必需Chain在CLK根记录中的冻结交接：commit或artifact、合同版本、端到端入口、数据身份、可执行检查及限制。
2. 仅从这些真实输入定稿Fusion GO列表和初始CELL；一条Fusion Chain可以包含一个或多个线性GO。
3. 进入`$small-loop-skill`并调用`$slk-select-models`；Fusion Chain 本身是一个完整的 SLK Loop，使用本Run固定的最新SLK版本完成CELL校准、模型选择、D0/D1/D2安排和成员交付准备，Owner指定仍有效。
4. 把定稿结果写入`SLK-RUN-<RUN-ID>-FUSION.md`，并在CLK根记录登记其输入集合和完成条件。

## 建立独立施工空间

Fusion在新的集成worktree和新分支中从本Run基线开始；这是新的独立worktree，装入每条施工Chain的D2通过候选、正式合同及必要数据。Fusion对代码重叠、实现冲突和接口适配承担最终集成责任，理解各候选的功能意图并构造完整系统；不把某条Chain当默认主线，也不把机械Git merge当作融合完成。前置Chain的临时端口、缓存、进程和可变施工残留不作为输入。

## 建立成员并测试通讯

1. Supervisor 创建Fusion Checker可见对话，交付Fusion记录、GO/CELL计划、冻结输入、合同和集成空间。
2. 完成Supervisor ↔ Checker双向通讯测试，并让Checker按SLK完成Checker理解确认。
3. Checker 创建Fusion Worker可见对话，交付首个CELL和所需上下文。
4. 完成Checker ↔ Worker双向通讯测试，并完成Supervisor ↔ Worker应急双向通讯测试。
5. 若成员或通道尚未准备好，建议由其上一级成员恢复或更换后重测，再由Checker派发首个CELL。

## 开工与边界

准备完成后启动这一条Fusion Chain。Checker与Worker按SLK推进一个或多个线性GO；共享Supervisor负责融合层协调及最终D2，不接管日常CELL派工或D1。

若真实融合暴露合同缺口，Supervisor记录证据并协调受影响的合同修订；产品目标、业务选择或Owner权限发生变化时，再向Owner提出一个清楚的问题。

## 完成后

当Fusion的全部GO已完成D0和D1并准备接受最终D2时，调用`$clk-close-run`。
