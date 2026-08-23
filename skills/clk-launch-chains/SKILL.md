---
name: clk-launch-chains
description: Use when an active Chain Loop Skill (CLK) Run has an accepted plan and a prepared Supervisor ready to create and synchronously launch all construction Chain teams.
---

# Launch the Construction Chains

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

建立所有可见的Chain成员，逐级证明通讯可用，并让全部 Chain准备完成后在同一施工周期同时启动。

## 准备记录与空间

1. Supervisor创建或核对根记录`CLK-RUN-<RUN-ID>-RECORD.md`，并从已确认方案创建结构权威`CLK-CHAIN-MAP.md`；只有Supervisor修改结构，所有成员可以读取，再登记Run、合同、隔离方案和计划总量。
2. 为每条Chain建立`SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md`，让后续成员各自记录事实、错误、返工、豁免和交付。
3. 按隔离方案准备每条Chain的施工空间，并核对正式合同身份与临时配置注入位置。

## 逐级建立成员

对每条Chain依次完成以下准备；这些准备可以并行推进，但建议在任何Chain派发首个CELL前汇总所有结果。

1. Supervisor 创建该Chain的可见Checker对话，交付Chain目标、线性GO/CELL计划、融合接口合同、隔离信息和记录路径。
2. 完成Supervisor ↔ Checker双向通讯测试：Supervisor发送带Run ID和Chain ID的测试消息，Checker在自己的可见对话中回复同一身份与职责摘要。
3. Checker按`$small-loop-skill`完成Checker 理解确认，并说明首个CELL的验收重点、隔离方式和记录位置。
4. Checker 创建 Worker可见对话，交付当前Chain规则与首个CELL上下文。
5. 完成Checker ↔ Worker双向通讯测试：Checker发送带CELL身份的测试消息，Worker回复所见目标、边界和交付对象。
6. 完成Supervisor ↔ Worker应急双向通讯测试：仅验证异常路线可用，不把Supervisor变成日常派工或D1角色。
7. 将成员身份、测试结果和准备状态写入对应Chain记录与CLK根记录。

若某个成员或通道未准备完成，建议由其上一级成员恢复或更换该成员，再重复对应通讯测试；其他Chain可以继续完成准备。

## 同步开工

全部 Chain成员、施工空间、合同和通讯准备完成后，Supervisor发出同一施工周期的启动信号。各Checker随即按SLK派发自己的首个CELL，使每条Chain作为一个完整SLK Loop同时启动并独立推进。

跨Chain事实通过冻结合同、正式记录或Supervisor协调，不建立成员横向日常通讯路线。每个角色交付后结束当前活动，不使用`wait_threads`或读取其他成员内部状态，下一条真实消息按需激活。各Checker与Worker继续SLK循环，Supervisor只处理CLK层协调、Chain D2和最终Fusion条件。

## 完成后

每条Chain持续更新自己的SLK记录；根记录只保留CLK级进度、合同修订、Chain D2结果和Fusion准备状态。
