---
name: clk-plan-run
description: Use when an active Chain Loop Skill (CLK) Run needs its concurrent Chain plan finalized before a new Supervisor is created.
---

# Plan a CLK Run

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

把本次中型或大型工程整理成可同时施工、能够最终融合的Run方案，并取得Owner对本Run建立和开工的确认。

## 建议做法

1. 检查并更新当前适用的CLK与SLK，让方案引用明确的方法版本。
2. 从真实项目基线写出本Run目标、边界、完成后结果和Owner关心的结论。未来Run的预案不当作当前已建立的Run。
3. 划分两条或以上相互独立的前置Chain。每条Chain有稳定职责，所有前置Chain能够在同一施工周期开始，不依赖另一Chain的未完成内部结果。
4. 为每条Chain规划线性GO和全部初始 CELL，说明交付成果及其与Fusion Chain的关系。
5. 进入`$small-loop-skill`并调用`$slk-select-models`，为共享Supervisor及各Checker、Worker选择能力，再结合模型、电脑、共享负载、累积工程量和余量校准每个初始CELL；本Run固定同一最新SLK版本，CLK不维护另一套模型表或模型Skill，Owner指定仍有效。
6. 调用`$clk-design-fusion-contracts`，形成每条Chain遵守的完整合同和可执行检查。
7. 调用`$clk-plan-parallel-isolation`，为所有Chain规划临时worktree、运行空间和并行资源。
8. 写出Fusion Chain的目标、正式输入、预期完整系统和初步GO轮廓。具体GO、初始 CELL及模型在真实Chain成果通过D2后定稿。
9. 汇总Chain、GO、初始CELL、合同、隔离、检验和Fusion轮廓，交给Owner确认本次CLK Run及开工；确认后的结构内容交由Supervisor创建和修改`CLK-CHAIN-MAP.md`。
10. Owner确认后，由原对话创建新的 Supervisor，完成原对话 ↔ Supervisor双向通讯测试并交付方案。原对话随后退出工程工作，仅保留Owner联系与Supervisor异常恢复入口。

## 完成后

新Supervisor使用`$clk-grill-supervisor`完成SLK与CLK两段理解确认，再建立本Run记录和成员。
