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
