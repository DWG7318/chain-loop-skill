---
name: clk-plan-parallel-isolation
description: Use when an active Chain Loop Skill (CLK) Run needs concurrent construction workspaces and temporary runtime bindings that preserve stable product contracts.
---

# Plan CLK Parallel Isolation

> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，不可脱离当前 CLK Run 单独使用。
> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 Checker、Worker 或 CELL 方法。

## 当前目标

让全部前置Chain在同一施工周期安全并行，同时保持：**逻辑合同保持稳定，物理施工隔离临时注入**。

## 建议规划

为每条Chain记录正式身份、临时绑定、配置注入位置、共享资源和清理方式。通常考虑：

- 独立Git worktree与施工分支；
- 独立构建、测试、临时输出和日志目录；
- 独立数据库、schema或测试数据副本；
- 独立端口、服务名称和进程；
- 独立缓存、浏览器profile、环境变量与测试凭据；
- 分配到本Chain的CPU、内存、磁盘、GPU、模型和其他资源。

只读且不变化的依赖可以共享。每条施工Chain只产生自己的D2通过候选，不合并其他Chain，也不作为默认集成主线；端口、路径、数据库名、账号等临时值通过配置、环境变量或测试夹具注入，不进入正式融合合同。

Chain数量与CELL大小参考电脑能够同时承载的真实负载和余量。长期争用同一不可隔离资源时，前期优先重新划分Chain或减少数量；短时物理资源可以协调具体命令，不把整条Chain改成串行施工。

可以从`assets/PARALLEL-ISOLATION-PLAN.template.md`建立方案。Supervisor在创建成员前确认所有工作空间和资源已经可用，再由`$clk-launch-chains`统一启动。

## D2与Fusion交接

Chain D2检查成果能够脱离临时环境，按正式合同重新部署和调用。Fusion Chain接收代码、冻结构建成果、合同和必要数据，不继承可变缓存、临时端口、测试凭据或施工进程。

前置Chain交接完成后，根据记录清理临时资源；Fusion Chain在新的worktree中建立完整系统的正式运行配置。
