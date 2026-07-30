from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "chain-loop-skill"


def contract() -> dict:
    return json.loads((SKILL / "contracts" / "clk-control-kernel.json").read_text(encoding="utf-8"))


def test_version_and_identity() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert version == "2.4.0"
    assert f"Current version: **{version}**" in (ROOT / "README.md").read_text(encoding="utf-8")
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "# Chain Loop Skill (CLK)" in text
    assert "name: chain-loop-skill" in text
    assert "$chain-loop-skill" in text
    assert f"Current specification version: `{version}`." in text


def test_contract_and_legacy() -> None:
    c = contract()
    assert c["method"] == "CLK"
    assert c["product_name"] == "Chain Loop Skill"
    assert c["version"] == "2.4.0"
    assert c["synchronization_unit"] == "LEVEL"
    assert c["legacy_identity"]["abbreviation"] == "MSLK"
    assert c["legacy_identity"]["formal_new_runs_allowed"] is False


def test_roles_calabash_and_chain_model() -> None:
    c = contract()
    assert c["role_types"] == ["SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"]
    assert c["calabash_gate"]["required"] is True
    assert c["calabash_gate"]["minimum_layers"] == ["GRANDPA", "PRODUCT_ARCHITECTURE", "ONTOLOGY"]
    model = c["multi_chain"]
    assert model["go_id_pattern"] == "GO-<LEVEL>-<CHAIN>"
    assert model["fixed_chain_roster"] is True
    assert model["full_level_barrier"] is True
    assert model["multiple_active_gos_across_chains"] is True
    assert model["max_active_gos_per_chain"] == 1
    assert model["partial_unlock"] is False
    assert model["grapher"] is False


def test_chain_roster_uses_the_maximum_valid_chain_count() -> None:
    c = contract()
    policy = c["chain_count_policy"]
    assert policy["selection_criterion"] == "MAXIMUM_VALID_CHAIN_COUNT"
    assert policy["run_and_go_granularity_frozen_before_derivation"] is True
    assert policy["resource_limits_reduce_activation_not_roster"] is True
    assert set(policy["validity_constraints"]) == {
        "STABLE_OWNERSHIP",
        "CHAIN_COHESION",
        "LEVEL_01_LAUNCH_INDEPENDENCE",
        "SAME_LEVEL_ACCEPTANCE_INDEPENDENCE",
        "MUTABLE_WRITE_ISOLATION",
        "STRICT_LOCAL_ORDER",
        "FULL_RUN_LEVEL_BARRIER_VALIDITY",
        "NO_ARTIFICIAL_SPLIT",
    }
    for path in (ROOT / "README.md", ROOT / "SPEC.md", SKILL / "SKILL.md"):
        assert "最大有效 Chain 数量" in path.read_text(encoding="utf-8"), path
    answers = json.loads(
        (SKILL / "evals" / "clk-readiness-answer-key.json").read_text(encoding="utf-8")
    )
    assert "最大有效CHAIN数量" in "\n".join(answers["answers"].values())


def test_authority_verification_and_autonomy() -> None:
    c = contract()
    assert c["product_write_authority"] == ["WORKER"]
    assert c["cell_acceptance_authority"] == ["CHECKER"]
    assert c["go_verdict_authority"] == ["VERIFICATION"]
    assert c["verification_policy"]["direct_checker_handoff"] is True
    assert c["verification_policy"]["supervisor_relay"] is False
    assert c["autonomy"]["routine_owner_authorization_required"] is False


def test_layered_verification_barrier_and_owner_contract() -> None:
    c = contract()
    assert c["run_verification_layers"] == ["D0", "D1", "D2", "LEVEL", "D3"]
    assert c["verification_economy"]["consume_lower_receipts"] is True
    assert c["verification_economy"]["blind_repetition"] is False
    assert c["level_verification"]["conditional_on_new_claim"] is True
    assert c["barrier_policy"]["formal_resolution_substitutes_required_d2"] is False
    assert set(c["barrier_policy"]["optional_terminal_states"]) == {
        "D2_PASS",
        "CANCELLED",
        "DEFERRED_BY_AMENDMENT",
        "SUPERSEDED",
    }
    assert c["owner_acceptance"]["scope"] == "RUN_PRODUCT_ONLY"
    assert c["owner_acceptance"]["project_security_closed"] is False
    assert c["owner_acceptance"]["delivery_authorized"] is False


def test_topology_fault_localization_is_clk_native_and_bounded() -> None:
    c = contract()
    policy = c["topology_fault_localization"]
    assert policy["fault_classes"] == [
        "CHAIN_LOCAL",
        "CROSS_CHAIN_COMPOSITION",
        "LEVEL_BARRIER",
    ]
    assert policy["one_active_hypothesis_per_fault_series"] is True
    assert policy["healthy_chain_requires_comparability_proof"] is True
    assert policy["healthy_chain_d2_substitution_allowed"] is False
    assert policy["healthy_chain_same_level_dependency_allowed"] is False
    assert policy["minimal_closure_uses_receipt_consumption"] is True
    assert policy["receipt_catalog_required"] is True
    assert policy["receipt_partition"] == "CATALOG_EQUALS_INVALIDATED_UNION_PRESERVED"
    assert policy["hypothesis_evidence_must_be_content_hash_bound"] is True
    assert policy["source_attempt_scope_bound_to_fault"] is True
    assert policy["healthy_control_must_match_preserved_catalog_d2"] is True
    assert policy["state_hypothesis_status"] == {
        "OPEN": "ACTIVE",
        "FALSIFIED": "FALSIFIED",
        "SUPERSEDED": "FALSIFIED",
        "ROUTED": "CONFIRMED",
        "RESOLVED": "CONFIRMED",
    }
    assert policy["native_routes"] == {
        "CHAIN_LOCAL": ["CELL_REWORK", "GO_REWORK_REQUIRED"],
        "CROSS_CHAIN_COMPOSITION": ["LEVEL_REVERIFICATION"],
        "LEVEL_BARRIER": ["BARRIER_RECALCULATION"],
    }
    assert policy["barrier_only_reverification_layers"] == ["BARRIER"]
    assert set(policy["escalation_routes"]) == {
        "PLAN_DEFECT",
        "CALABASH_REVIEW_REQUIRED",
        "METHOD_BOUNDARY_EXCEEDED",
    }
    assert c["role_types"] == ["SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"]
    assert c["run_verification_layers"] == ["D0", "D1", "D2", "LEVEL", "D3"]
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["topology_fault_classes"] == policy["fault_classes"]
    answers = json.loads(
        (SKILL / "evals" / "clk-readiness-answer-key.json").read_text(encoding="utf-8")
    )
    assert "CHAIN_LOCAL、CROSS_CHAIN_COMPOSITION、LEVEL_BARRIER" in "\n".join(
        answers["answers"].values()
    )


def test_canonical_agent_and_new_references_are_packaged() -> None:
    agent = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "Chain Loop Skill (CLK)" in agent
    assert "$chain-loop-skill" in agent
    for name in (
        "run-lifecycle-and-verification.md",
        "receipt-and-state-contracts.md",
        "lccoding-interface.md",
    ):
        assert (SKILL / "references" / name).is_file()


def test_go_boundary_and_detection() -> None:
    c = contract()
    assert c["cross_go_rule"]["cell_to_cell_dependency_allowed"] is False
    assert c["cross_go_rule"]["same_level_dependency_allowed"] is False
    assert c["detection_tiers"] == ["CELL_ALWAYS", "CELL_TRIGGERED", "GO_BOUNDARY", "PROJECT_FINAL"]


def test_line_budgets() -> None:
    paths = [ROOT / "README.md", ROOT / "CHANGELOG.md", SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
    for path in paths:
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 1000, path


def test_readiness_count() -> None:
    q = json.loads((SKILL / "evals" / "clk-readiness-questions.json").read_text(encoding="utf-8"))
    a = json.loads((SKILL / "evals" / "clk-readiness-answer-key.json").read_text(encoding="utf-8"))
    assert len(q["questions"]) == 25
    assert len(a["answers"]) == 25
    assert {x["id"] for x in q["questions"]} == set(a["answers"])
