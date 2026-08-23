---
name: clk-close-run
description: Use when the Fusion Chain in an active Chain Loop Skill (CLK) Run is ready for final D2, archival, and one concise Owner conclusion.
---

# Close the CLK Run

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

让共享Supervisor按`$small-loop-skill`完成Fusion D2；这次判断就是CLK Run的最终D2，并产生一份可查询的完工记录和一个Owner结论。

## 最终判断

1. Fusion Checker交付干净的最终D2包：Run目标、各Chain冻结输入、Fusion GO结果、完整系统候选、端到端入口、融合合同、可执行检查及客观环境事实。
2. Supervisor先从候选、合同和可观察事实形成独立判断，再读取D0、D1、返工、豁免和记录历史核对遗漏与一致性。
3. 检查前置Chain成果是否真实接入，Fusion GO是否组合成完整系统，合同、数据、安全、运行配置和交付入口是否互相一致。
4. 若结果尚需修复，按SLK返回Fusion Checker → Fusion Worker → Fusion Checker处理；共享Supervisor在新候选形成后重新执行最终判断。

## 记录结论

最终D2通过后，在`CLK-RUN-<RUN-ID>-RECORD.md`汇总：

- Run目标、Chain数量、各Chain D2和冻结输入；
- Fusion的D0、D1、D2结果与完整系统身份；
- 错误、返工、豁免、已知限制和未来恢复条件；
- 合同版本、证据路径、交付入口和归档位置。

各SLK记录继续保存成员自己的详细事实，CLK根记录只汇总可追溯结论，不重复复制整段过程。

## 归档与Owner回报

交付和记录核对完成后，先归档Fusion Worker，再归档Fusion Checker，并保留Supervisor及其当前Run上下文供Owner查询。

向Owner发送一个简洁结论，例如：

> CLK Run已完成；3/3施工Chain及Fusion的D0、D1、D2均已通过。豁免1项，已知限制见记录。完整记录：`<path>`。

该结论提供事实，不要求Owner再次验收方法过程，也不自动建立或启动下一个CLK Run。未来Run由原对话结合本次真实交付基线重新定稿、取得Owner确认并创建新的Supervisor。
