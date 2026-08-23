---
name: clk-complete-chain
description: Use when one construction Chain in an active Chain Loop Skill (CLK) Run is ready for the shared Supervisor to perform its isolated D2 and prepare a frozen Fusion handoff.
---

# Complete One Construction Chain

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

由共享Supervisor按`$small-loop-skill`的D2语义独立检查一条施工Chain；通过后把结果冻结为Fusion输入，未通过时只把工作退回所属Chain。

## 初始材料

所属Checker先交付干净的初始 D2 包，建议只包含：

- Chain目标与各GO结果；
- 冻结候选身份，包括commit或artifact、版本与可复现定位；
- 已验证的端到端入口；
- 当前融合接口合同、合同版本与可执行合同检查；
- 判断结果所需的客观环境事实和可移植证据。

初始包不以施工者结论或说服性摘要代替候选和事实。

## 隔离判断

1. Supervisor先从初始包和可观察工程事实形成独立 D2 判断。
2. 判断重点包括GO组合是否形成Chain目标、合同符合性、可执行合同检查结果，以及候选离开临时施工环境后的可移植性。
3. 初步判断形成后，再读取D0、D1、Worker推理、Checker说明、返工、豁免和完整记录，用于发现遗漏事实并核对记录一致性。
4. 若后续材料推翻初步判断，记录改变判断的具体证据，而不是继承成员结论。

## 结果路线

### D2未通过

把具体问题、可复现证据和建议修复范围交回所属Checker，由Checker → Worker → Checker完成该Chain的SLK返工与D1。其他独立Chain继续施工或完成自己的D2；涉及共享合同的事实由Supervisor记录并判断影响范围。

### D2 PASS

1. 冻结commit、artifact、合同版本、端到端入口、检查结果和必要数据身份。
2. 在该Chain的SLK记录中写入D2结论、证据、豁免和Fusion交接位置。
3. 在`CLK-RUN-<RUN-ID>-RECORD.md`登记正式Fusion输入，不向Owner报告中间完工。
4. 完成交接后先归档Worker，再归档Checker，并保留共享Supervisor继续处理其他Chain与Fusion。

## 完成后

当所有必需施工Chain都有D2 PASS冻结交接时，调用`$clk-start-fusion`；否则共享Supervisor退出当前检查动作，等待下一条真实事件再恢复工作。
