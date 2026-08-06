from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "chain-loop-skill"


def contract() -> dict:
    return json.loads((SKILL / "contracts" / "clk-control-kernel.json").read_text(encoding="utf-8"))


def test_version_and_identity() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert version == "2.6.0"
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
    assert c["version"] == "2.6.0"
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


def test_worker_wake_patrol_task_identity_and_layered_progress_are_bounded() -> None:
    c = contract()
    wake = c["worker_wake_ladder"]
    assert wake["actor"] == "WORKER"
    assert wake["target"] == "ORIGINALLY_BOUND_CHECKER"
    assert wake["offset_minutes"] == [0, 2, 4, 6]
    assert wake["max_wait_minutes_per_level"] == 2
    assert wake["message_requires"] == [
        "GO_ID",
        "CELL_ORDINAL",
        "REQUIRED_CELL_TOTAL",
        "DELIVERED_OR_BLOCKED_OR_EXECUTION_FAILURE",
    ]
    assert wake["general_role_message_bus"] is False
    assert wake["dispatch_requires_complete_wake_lifecycle"] is True
    assert wake["initial_undispatched_may_have_no_wake"] is True
    assert wake["worker_signal_requires_matching_dispatch"] is True
    assert all(wake["dispatch_capability_preflight"].values())

    wait = c["supervisor_wait_policy"]
    assert wait["wait_threads_allowed"] is False
    assert wait["wait_threads_loop_allowed"] is False
    assert wait["timeout_zero_snapshot_allowed"] is True

    patrol = c["run_patrol"]
    assert patrol["count_per_run"] == 1
    assert patrol["heartbeat_count_per_run"] == 1
    assert patrol["conversation_type"] == "RUN_PATROL_CONVERSATION"
    assert patrol["model"] == "gpt-5.6-terra"
    assert patrol["reasoning_effort"] == "xhigh"
    assert patrol["interval_minutes"] == [10, 15, 30]
    assert patrol["project_workload_interval_minutes"] == {
        "LOW": 10,
        "MEDIUM": 15,
        "HIGH": 30,
    }
    assert patrol["canonical_technical_role"] is False
    assert patrol["set_thread_pinned"] is False
    assert patrol["mechanical_checks"] == [
        "UNEXPLAINED_STALL",
        "PENDING_WAKE",
        "SUBAGENT_EVIDENCE",
        "SUPERVISOR_WAIT",
        "DUPLICATE_PATROL_OR_HEARTBEAT",
        "THREAD_PIN_PROVENANCE",
        "TERMINAL_NOT_CLOSED",
    ]
    assert patrol["status_and_alerts_require_observation_and_evidence_identity"] is True
    assert patrol["authoritative"] is False
    assert patrol["technical_acceptance"] is False
    assert patrol["product_work"] is False

    model_policy = c["model_selection_policy"]
    assert model_policy["default_model"] == "gpt-5.6-terra"
    assert model_policy["default_reasoning_effort"] == "xhigh"
    assert model_policy["fine_grained_low_risk_worker_model"] == "gpt-5.6-luna"
    assert model_policy["exceptional_correction_model"] == "gpt-5.6-sol"
    assert model_policy["patrol_uses_default_policy"] is True
    assert model_policy["gpt_5_5_and_lower_allowed"] is False
    assert model_policy["ultra_requires_item_specific_owner_authorization"] is True
    assert model_policy["silent_model_switch_allowed"] is False
    assert model_policy["capability_equivalence_required_for_alternatives"] is True
    assert model_policy["switch_requires_new_binding_and_fresh_readiness_isolation_verification"] is True
    assert model_policy["same_model_role_isolation_required"] is True

    run_control = yaml.safe_load((SKILL / "templates" / "run-control-trace.yaml").read_text(encoding="utf-8"))
    model_ledger = yaml.safe_load((SKILL / "templates" / "model-binding-ledger.yaml").read_text(encoding="utf-8"))
    patrol_binding = next(item for item in model_ledger["bindings"] if item["role_kind"] == "PATROL")
    assert run_control["patrols"][0]["model_binding_id"] == patrol_binding["binding_id"]
    assert run_control["patrols"][0]["model"] == patrol_binding["actual_model"]

    identity = c["task_identity"]
    assert identity["subtask_examples"] == ["GO", "CELL", "ROUND", "PLAN_STEP"]
    assert identity["visible_peer_task_is_subagent"] is False
    assert identity["subagent_capabilities"] == [
        "spawn_agent",
        "delegate_task",
        "hidden_agent",
        "background_agent",
    ]

    progress = c["layered_progress"]
    assert progress["hard_rule_number"] == 5
    assert progress["cell_numerator_source"] == "CURRENT_EFFECTIVE_D1_PASS_RECEIPTS"
    assert progress["go_numerator_source"] == "CURRENT_D2_GO_VERIFIED_VERDICTS"
    assert progress["denominator_source"] == "CURRENT_VERSIONED_REQUIRED_SET"
    assert progress["worker_delivery_increments_accepted"] is False
    assert progress["checker_cell_noise_to_supervisor"] is False
    assert progress["verification_continuous_progress"] is False
    assert progress["patrol_engineering_progress"] is False
    assert progress["every_d1_decision_has_exactly_one_checker_progress"] is True
    assert progress["checker_progress_binds_d1_event_and_receipt"] is True
    assert progress["every_material_trigger_has_exactly_one_supervisor_progress"] is True
    assert progress["trigger_reuse_or_omission_allowed"] is False
    assert progress["states"] == [
        "DELIVERED",
        "D1_ACCEPTED",
        "GO_CANDIDATE_READY",
        "D2_VERIFIED",
        "RUN_VERIFIED",
        "OWNER_ACCEPTED",
    ]

    capacity = c["cell_capacity"]
    assert capacity["hard_rule_number"] == 6
    assert capacity["supervisor_owns_device_and_cumulative_load"] is True
    assert capacity["checker_runs_pre_dispatch_gate"] is True
    assert capacity["gate_results"] == ["PASS", "SPLIT_REQUIRED", "CAPACITY_BLOCKED"]
    assert capacity["dispatch_requires"] == "CURRENT_CELL_CAPACITY_GATE_PASS"
    assert capacity["unknown_capability_result"] == "CAPACITY_BLOCKED"
    assert capacity["worker_may_split"] is False
    assert capacity["worker_scope_signal"] == "CELL_SCOPE_EXCEEDED"
    assert capacity["post_dispatch_split_signal"] == "POST_DISPATCH_CELL_SPLIT"
    assert capacity["three_or_more_post_dispatch_successors"] == "CELL_OVERSIZE_SEVERE"
    assert capacity["six_seven_eight_are_always_severe"] is True
    assert capacity["logical_level_parallelism_equals_device_concurrency"] is False

    pin = c["thread_pin_policy"]
    assert pin["hard_rule_number"] == 7
    assert pin["method_role_may_pin"] is False
    assert pin["patrol_may_pin_or_unpin"] is False
    assert pin["legal_provenance"] == ["OWNER_UI", "OWNER_EXPLICIT_AUTHORIZATION"]
    assert pin["agent_violation"] == "UNAUTHORIZED_THREAD_PIN"
    assert pin["unknown_provenance"] == "PIN_PROVENANCE_UNKNOWN"
    assert pin["pin_then_unpin_clears_violation"] is False
    assert pin["archive_lifecycle_independent"] is True


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
    assert policy["one_candidate_per_affected_chain"] is True
    assert policy["canonical_candidate_go_identity"] == "GO-<LEVEL>-<CHAIN>"
    assert policy["issuer_authority"] == {
        "CHAIN_LOCAL": {"responsibility": "CHECKER", "scope": "AFFECTED_CHAIN"},
        "CROSS_CHAIN_COMPOSITION": {"responsibility": "SUPERVISOR", "scope": "LEVEL"},
        "LEVEL_BARRIER": {"responsibility": "SUPERVISOR", "scope": "LEVEL"},
    }
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
    assert manifest["topology_fault_identity"] == {
        "candidate_binding": "ONE_CANONICAL_GO_PER_AFFECTED_CHAIN",
        "issuer_authority": policy["issuer_authority"],
    }
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
        "worker-wake-patrol-and-progress.md",
        "model-selection-and-binding.md",
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
    joined = "\n".join(a["answers"].values())
    for marker in (
        "T+0、T+2、T+4、T+6",
        "gpt-5.6-terra+xhigh",
        "gpt-5.6-luna+xhigh",
        "gpt-5.6-sol+xhigh",
        "PROVEN_EQUIVALENT",
        "SILENT_MODEL_SWITCH",
        "wait_threads",
        "spawn_agent、delegate_task、隐藏Agent、后台Agent",
        "第五项硬规则",
        "DELIVERED不等于D1_ACCEPTED",
        "GO_CANDIDATE_READY不等于D2_VERIFIED",
        "第六项硬规则",
        "DEVICE_CAPACITY_PROFILE",
        "CELL_CAPACITY_GATE",
        "CELL_OVERSIZE_SEVERE",
        "第七项硬规则",
        "UNAUTHORIZED_THREAD_PIN",
        "PIN_PROVENANCE_UNKNOWN",
        "LOW→10、MEDIUM→15、HIGH→30",
    ):
        assert marker in joined
