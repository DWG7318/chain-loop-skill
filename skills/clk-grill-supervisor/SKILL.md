---
name: clk-grill-supervisor
description: Use when a newly created Supervisor for an active Chain Loop Skill (CLK) Run needs to demonstrate SLK and CLK understanding before creating the Chain teams.
---

# Grill the CLK Supervisor

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

让新Supervisor先证明自己理解每条Chain怎样按SLK施工，再证明自己理解CLK怎样组织并行Chain和最终Fusion Chain。

## 建议顺序

1. 先读取`$chain-loop-skill`及已确认的CLK Run方案，复述本Run目标、Chain划分和自己的边界。
2. 按CLK入口进入`$small-loop-skill`，完成其中的SLK Supervisor Grill，理解线性GO/CELL、Checker与Worker关系、D0/D1/D2、返工、记录、通讯和归档。
3. SLK理解通过后返回 CLK，再进行本Skill的问答。

## CLK问答

一次只问一个问题；根据回答质量动态决定下一题，不设置固定题数。问题从本Run事实中抽取，建议覆盖：

- 各Chain的职责、Chain 独立性，以及为什么能够在同一施工周期启动；
- 每条Chain如何执行SLK，共享Supervisor与各Checker、Worker怎样配合，以及各角色为什么在交付后结束当前活动而不使用`wait_threads`或观察其他成员施工过程；
- 融合接口合同怎样约束施工、修订、可执行检查和交接；
- 临时隔离怎样保护并行施工，又怎样避免污染正式合同与Fusion输入；
- Supervisor怎样以隔离方式完成Chain D2，以及局部失败如何回到对应Checker处理；
- 全部前置Chain通过后，怎样定稿并启动Fusion Chain；
- 当合同冲突、资源冲突或现实证据推翻计划时，怎样保持Run继续推进。

回答不充分时，先指出具体误解并给出纠正材料，再请Supervisor解释正确处理方式。以能够结合当前Run作出一致、可执行判断作为理解证据。

## 完成后

把问答结论和仍需留意的风险写入`CLK-RUN-<RUN-ID>-RECORD.md`，然后调用`$clk-launch-chains`建立各Chain成员并完成开工准备。
