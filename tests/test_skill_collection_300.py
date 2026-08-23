from __future__ import annotations

from skill_testkit import (
    EXPECTED_CHILDREN,
    EXPECTED_SKILLS,
    ROOT,
    SKILLS,
    assert_skill_shape,
    read_skill,
    size_diagnostics,
)


def test_version_is_300() -> None:
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "3.0.2"


def test_collection_has_one_main_and_eight_children() -> None:
    actual = (
        tuple(sorted(path.name for path in SKILLS.iterdir() if path.is_dir()))
        if SKILLS.is_dir()
        else ()
    )
    assert actual == tuple(sorted(EXPECTED_SKILLS))


def test_all_skills_have_discoverable_frontmatter_and_advisory_language() -> None:
    diagnostics: list[str] = []
    for name in EXPECTED_SKILLS:
        assert_skill_shape(name)
        diagnostics.extend(size_diagnostics(name, read_skill(name)))
    assert diagnostics == [], "\n".join(diagnostics)


def test_main_routes_to_every_clk_child_and_enters_slk_main() -> None:
    text = read_skill("chain-loop-skill")
    for child in EXPECTED_CHILDREN:
        assert text.count(f"`${child}`") == 1, child
    assert text.count("`$small-loop-skill`") >= 1
    assert "`$slk-" not in text


def test_main_keeps_the_owner_approved_clk_core() -> None:
    text = read_skill("chain-loop-skill")
    for marker in (
        "中型或大型",
        "一个 CLK",
        "Run",
        "两条",
        "Chain",
        "同一施工周期",
        "SLK",
        "共享 Supervisor",
        "Checker",
        "Worker",
        "D0",
        "D1",
        "D2",
        "Fusion Chain",
        "一个或多个 GO",
        "CLK-RUN-<RUN-ID>-RECORD.md",
    ):
        assert marker in text


def test_main_keeps_clk_at_project_scope_and_slk_at_chain_scope() -> None:
    text = read_skill("chain-loop-skill")
    assert "项目层使用 CLK" in text
    assert "Chain 施工使用 SLK" in text
    assert "原对话" in text
    assert "Owner" in text
    assert "Supervisor" in text
    assert "Checker 和 Worker" in text


def test_every_child_declares_its_clk_only_usage_boundary() -> None:
    boundary = (
        "> **使用边界：** 本 Skill 是 Chain Loop Skill（CLK）的子 Skill，"
        "不可脱离当前 CLK Run 单独使用。\n"
        "> 由 `$chain-loop-skill` 路由到本情境；本 Skill 不替代 SLK 的 "
        "Checker、Worker 或 CELL 方法。"
    )
    for child in EXPECTED_CHILDREN:
        text = read_skill(child)
        frontmatter, body = text[4:].split("\n---\n", 1)
        assert "Chain Loop Skill (CLK) Run" in frontmatter, child
        assert boundary in body, child
        assert body.index(boundary) < body.index("## "), child
    assert boundary not in read_skill("chain-loop-skill")


def test_active_collection_does_not_restore_the_legacy_clk_kernel() -> None:
    legacy = (
        "Control Conversation",
        "Verifier responsibility",
        "Run Patrol",
        "RUN_PATROL",
        "GO-scoped Verification",
        "D3",
        "Stage",
        "LEVEL-",
        "model-binding-ledger",
        "runtime-state-index",
    )
    for name in EXPECTED_SKILLS:
        text = read_skill(name)
        for marker in legacy:
            assert marker not in text, f"{name}: {marker}"


def test_collection_has_one_shared_supervisor_and_no_clk_role_expansion() -> None:
    text = read_skill("chain-loop-skill")
    assert "共享一个 Supervisor" in text
    assert "每条前置 Chain" in text
    assert "独立 Checker" in text
    assert "独立 Worker" in text
    assert "Chain Supervisor" not in text
    assert not (SKILLS / "clk-check-cell").exists()
    assert not (SKILLS / "clk-execute-cell").exists()
    assert not (SKILLS / "clk-select-models").exists()


def test_topology_is_concurrent_construction_then_one_fusion_chain() -> None:
    text = read_skill("chain-loop-skill")
    assert text.index("两条或以上") < text.index("同一施工周期")
    assert "所有前置 Chain" in text
    assert "同时" in text
    assert "一条 Fusion Chain" in text
    assert "一个或多个 GO" in text
    assert "Stage" not in text
    assert "Level" not in text


def test_plan_run_builds_the_owner_confirmed_concurrent_run_before_handoff() -> None:
    text = read_skill("clk-plan-run")
    for marker in (
        "更新",
        "CLK",
        "SLK",
        "Run",
        "两条或以上",
        "Chain",
        "同一施工周期",
        "GO",
        "初始 CELL",
        "模型",
        "电脑",
        "共享负载",
        "余量",
        "$small-loop-skill",
        "$clk-design-fusion-contracts",
        "$clk-plan-parallel-isolation",
        "Fusion Chain",
        "Owner",
        "新的 Supervisor",
        "原对话 ↔ Supervisor",
        "退出工程工作",
    ):
        assert marker in text
    assert text.index("Owner") < text.index("新的 Supervisor")


def test_fusion_contract_skill_and_asset_are_complete_and_executable() -> None:
    text = read_skill("clk-design-fusion-contracts")
    for marker in (
        "能力",
        "API",
        "函数",
        "MCP",
        "事件",
        "数据结构",
        "样例",
        "状态",
        "生命周期",
        "错误",
        "权限",
        "安全",
        "持久化",
        "一致性",
        "版本",
        "兼容",
        "性能",
        "并发",
        "Fusion Chain",
        "可执行",
        "D2",
        "Supervisor",
        "Owner",
        "修订",
    ):
        assert marker in text
    asset = (
        SKILLS
        / "clk-design-fusion-contracts"
        / "assets"
        / "FUSION-INTERFACE-CONTRACT.template.md"
    )
    assert asset.is_file()
    asset_text = asset.read_text(encoding="utf-8")
    for heading in (
        "# Fusion Interface Contract",
        "## 身份与版本",
        "## 能力与调用",
        "## 数据、状态与错误",
        "## 权限、安全与持久化",
        "## 版本、性能与并发",
        "## 可执行合同检查",
        "## Fusion 接入与 Chain D2",
        "## 修订历史",
    ):
        assert heading in asset_text


def test_parallel_isolation_is_temporary_and_does_not_change_the_contract() -> None:
    text = read_skill("clk-plan-parallel-isolation")
    for marker in (
        "逻辑合同保持稳定，物理施工隔离临时注入",
        "worktree",
        "分支",
        "构建",
        "数据库",
        "schema",
        "端口",
        "服务",
        "进程",
        "缓存",
        "日志",
        "浏览器",
        "环境变量",
        "凭据",
        "资源",
        "配置",
        "D2",
        "Fusion Chain",
        "临时",
    ):
        assert marker in text
    asset = (
        SKILLS
        / "clk-plan-parallel-isolation"
        / "assets"
        / "PARALLEL-ISOLATION-PLAN.template.md"
    )
    assert asset.is_file()
    asset_text = asset.read_text(encoding="utf-8")
    for marker in (
        "Chain ID",
        "正式身份",
        "临时绑定",
        "注入位置",
        "只读共享",
        "清理",
        "Fusion 交接",
    ):
        assert marker in asset_text


def test_supervisor_proves_slk_then_clk_understanding_before_launch() -> None:
    text = read_skill("clk-grill-supervisor")
    for marker in (
        "一次只问一个问题",
        "动态决定",
        "不设置固定题数",
        "$chain-loop-skill",
        "$small-loop-skill",
        "SLK Supervisor Grill",
        "返回 CLK",
        "Chain 独立性",
        "融合接口合同",
        "临时隔离",
        "Chain D2",
        "Fusion Chain",
        "合同冲突",
        "纠正",
        "解释",
    ):
        assert marker in text
    assert text.index("$chain-loop-skill") < text.index("$small-loop-skill")
    assert text.index("SLK Supervisor Grill") < text.index("返回 CLK")
    assert "在线等待" not in text


def test_launch_waits_for_every_visible_pair_then_starts_all_chains_together() -> None:
    text = read_skill("clk-launch-chains")
    for marker in (
        "CLK-RUN-<RUN-ID>-RECORD.md",
        "SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md",
        "施工空间",
        "Supervisor 创建",
        "Supervisor ↔ Checker",
        "Checker 理解",
        "Checker 创建 Worker",
        "Checker ↔ Worker",
        "Supervisor ↔ Worker",
        "应急",
        "全部 Chain",
        "准备完成",
        "同一施工周期",
        "同时启动",
    ):
        assert marker in text
    assert text.index("全部 Chain") < text.index("同时启动")
    assert "Checker ↔ Checker" not in text
    assert "Worker ↔ Worker" not in text
    assert "Patrol" not in text
    assert "在线等待" not in text


def test_complete_chain_preserves_isolated_slk_d2_input_order() -> None:
    text = read_skill("clk-complete-chain")
    for marker in (
        "$small-loop-skill",
        "干净的初始 D2 包",
        "Chain目标",
        "GO结果",
        "冻结候选身份",
        "端到端入口",
        "融合接口合同",
        "可执行合同检查",
        "客观环境事实",
        "独立 D2 判断",
        "D0",
        "D1",
        "返工",
        "豁免",
    ):
        assert marker in text
    assert text.index("独立 D2 判断") < text.index("D0")
    assert text.index("独立 D2 判断") < text.index("D1")
    assert text.index("独立 D2 判断") < text.index("返工")


def test_complete_chain_routes_failure_locally_and_freezes_a_passed_handoff() -> None:
    text = read_skill("clk-complete-chain")
    for marker in (
        "GO组合",
        "合同符合性",
        "可移植性",
        "Checker → Worker → Checker",
        "其他独立Chain继续",
        "D2 PASS",
        "commit",
        "artifact",
        "合同版本",
        "冻结",
        "先归档Worker",
        "再归档Checker",
        "保留共享Supervisor",
        "CLK-RUN-<RUN-ID>-RECORD.md",
        "Fusion输入",
        "不向Owner报告中间完工",
    ):
        assert marker in text


def test_fusion_starts_from_real_frozen_inputs_after_supervisor_planning() -> None:
    text = read_skill("clk-start-fusion")
    for marker in (
        "所有必需施工Chain",
        "D2 PASS",
        "冻结交接",
        "定稿Fusion GO",
        "初始CELL",
        "$small-loop-skill",
        "模型选择",
        "新的集成worktree",
        "新分支",
        "Supervisor 创建Fusion Checker",
        "Supervisor ↔ Checker",
        "Checker理解",
        "Checker 创建Fusion Worker",
        "Checker ↔ Worker",
        "Supervisor ↔ Worker",
        "应急",
        "一条Fusion Chain",
        "一个或多个线性GO",
        "SLK-RUN-<RUN-ID>-FUSION.md",
    ):
        assert marker in text
    assert text.index("定稿Fusion GO") < text.index("Supervisor 创建Fusion Checker")
    assert text.index("Supervisor 创建Fusion Checker") < text.index("Checker 创建Fusion Worker")
    assert "Stage" not in text
    assert "Level" not in text


def test_final_fusion_d2_is_the_single_clk_run_closure() -> None:
    text = read_skill("clk-close-run")
    for marker in (
        "$small-loop-skill",
        "Fusion D2",
        "CLK Run的最终D2",
        "D0",
        "D1",
        "D2",
        "Chain数量",
        "豁免",
        "限制",
        "证据路径",
        "先归档Fusion Worker",
        "再归档Fusion Checker",
        "保留Supervisor",
        "Owner",
        "简洁结论",
        "不自动建立或启动下一个CLK Run",
    ):
        assert marker in text
    assert "更高检验层" not in text


def test_cross_skill_order_matches_the_approved_clk_graph() -> None:
    plan = read_skill("clk-plan-run")
    grill = read_skill("clk-grill-supervisor")
    launch = read_skill("clk-launch-chains")
    complete = read_skill("clk-complete-chain")
    fusion = read_skill("clk-start-fusion")
    close = read_skill("clk-close-run")

    assert plan.index("原对话 ↔ Supervisor") < plan.index("退出工程工作")
    assert grill.index("$chain-loop-skill") < grill.index("$small-loop-skill")
    assert grill.index("SLK Supervisor Grill") < grill.index("返回 CLK")

    ready = launch.index("全部 Chain成员、施工空间、合同和通讯准备完成后")
    for route in ("Supervisor ↔ Checker", "Checker ↔ Worker", "Supervisor ↔ Worker"):
        assert launch.index(route) < ready
    assert launch.index("准备完成后") < launch.index("同时启动")

    assert "SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md" in launch
    assert "SLK-RUN-<RUN-ID>-FUSION.md" in fusion
    assert "不向Owner报告中间完工" in complete
    assert fusion.index("定稿Fusion GO") < fusion.index("Supervisor 创建Fusion Checker")
    assert close.index("Owner") < close.index("不自动建立或启动下一个CLK Run")


def test_root_record_template_keeps_summary_links_without_copying_member_logs() -> None:
    main = read_skill("chain-loop-skill")
    record = (
        SKILLS / "chain-loop-skill" / "assets" / "CLK-RUN.template.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "CLK-RUN-<RUN-ID>-RECORD.md",
        "SLK-RUN-<RUN-ID>-CHAIN-<CHAIN-ID>.md",
        "SLK-RUN-<RUN-ID>-FUSION.md",
    ):
        assert marker in main
        assert marker in record
    for marker in (
        "Owner确认",
        "共享Supervisor",
        "同一施工周期",
        "合同版本",
        "临时隔离",
        "Chain D2",
        "冻结交接",
        "错误、返工与豁免",
        "归档状态",
        "Owner结论",
    ):
        assert marker in record
    assert "成员详细记录只保存在对应SLK记录" in record


def test_active_skills_do_not_reintroduce_ambiguous_authority_or_fixed_runtime() -> None:
    forbidden = (
        "Chain Supervisor",
        "Checker读取CLK",
        "Worker读取CLK",
        "Fusion Checker定稿",
        "Checker ↔ Checker",
        "Worker ↔ Worker",
        "`$slk-",
        "Supervisor派发CELL",
        "Supervisor执行D1",
        "gpt-",
        "claude-",
        "gemini-",
        "Pin",
        "runtime kernel",
    )
    for name in EXPECTED_SKILLS:
        text = read_skill(name)
        for marker in forbidden:
            assert marker not in text, f"{name}: {marker}"


def test_clk_roles_end_their_turn_instead_of_waiting_on_or_watching_chains() -> None:
    main = read_skill("chain-loop-skill")
    grill = read_skill("clk-grill-supervisor")
    launch = read_skill("clk-launch-chains")
    complete = read_skill("clk-complete-chain")
    fusion = read_skill("clk-start-fusion")
    active = "\n".join(read_skill(name) for name in EXPECTED_SKILLS)

    for stale in ("等待下一条真实事件", "在线等待", "持续观察"):
        assert stale not in active
    for text in (main, launch, complete):
        assert "结束当前活动" in text
        assert "不使用`wait_threads`" in text
    assert "真实消息重新激活" in main
    assert "下一条真实消息按需激活" in launch
    assert "不读取其他Chain施工状态" in complete
    assert "观察其他成员施工过程" in grill
    assert "Loop Engineering 的复合形态" in main
    assert "每条前置 Chain 都是一个完整的 SLK Loop" in main
    assert "Fusion Chain 也是一个完整的 SLK Loop" in main
    assert "消息只传输 Loop 工作和结果" in main
    assert "每条Chain作为一个完整SLK Loop" in launch
    assert "Fusion Chain 本身是一个完整的 SLK Loop" in fusion


def test_clk_wait_clarification_does_not_add_skill_lines() -> None:
    expected = {
        "chain-loop-skill": 37,
        "clk-close-run": 41,
        "clk-complete-chain": 49,
        "clk-design-fusion-contracts": 40,
        "clk-grill-supervisor": 37,
        "clk-launch-chains": 43,
        "clk-plan-parallel-isolation": 36,
        "clk-plan-run": 30,
        "clk-start-fusion": 42,
    }
    actual = {name: len(read_skill(name).splitlines()) for name in EXPECTED_SKILLS}
    assert actual == expected
