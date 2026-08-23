---
name: clk-design-fusion-contracts
description: Use when an active Chain Loop Skill (CLK) Run needs complete integration contracts before concurrent Chains begin or when engineering evidence requires a recorded revision.
---

# Design CLK Fusion Contracts

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

为每条前置Chain建立完整、详细、可执行的融合接口合同，让各Chain独立施工后能够由Fusion Chain真实接入。

## 合同内容

根据项目实际情况说明：

- 合同身份、版本、提供方、使用方与适用Chain；
- 对外能力，以及API、函数、MCP、事件或其他调用方式；
- 数据结构、字段、类型、样例、状态与生命周期；
- 错误、异常、失败返回和恢复语义；
- 权限、安全、敏感数据、持久化、共享与一致性边界；
- 版本与兼容策略，以及性能、资源和并发预期；
- Fusion Chain如何接入候选身份、输出接口、功能意图与冲突敏感范围，以及最终交付物和Chain D2验收结果；
- schema、夹具、模拟调用端、预期结果等可执行合同检查。

可以从`assets/FUSION-INTERFACE-CONTRACT.template.md`建立项目合同。合同描述正式产品身份，不写入临时端口、路径、数据库名或测试凭据。

## 施工与修订

Checker和Worker按当前合同版本推进SLK，并在适合的D1中复用合同检查。Chain D2完整检查GO组合、合同符合性、可调用性和交付完整性。

施工事实表明合同存在技术问题时，Checker把证据与建议交给Supervisor。Supervisor在Owner已确认的Run结果内形成有记录的修订，通知受影响Chain，并让后续施工和D2引用新版本。

修订改变产品目标、业务选择或Owner掌握的权限时，Supervisor先整理推荐方案和影响，再向Owner提出一个清楚问题。其他技术修订由Supervisor协调，不把问题原样退回Owner。

## 完成后

合同位置和版本写入CLK根记录、各Chain方案及可执行检查入口，再回到`$clk-plan-run`完成本Run确认。
