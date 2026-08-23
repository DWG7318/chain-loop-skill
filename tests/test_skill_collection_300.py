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
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "3.0.0"


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
    assert "每条 Chain" in text
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
