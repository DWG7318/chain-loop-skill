from __future__ import annotations

import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_run_control.py"
PATROL_CHECKS = [
    "UNEXPLAINED_STALL",
    "PENDING_WAKE",
    "SUBAGENT_EVIDENCE",
    "SUPERVISOR_WAIT",
    "DUPLICATE_PATROL_OR_HEARTBEAT",
    "THREAD_PIN_PROVENANCE",
    "TERMINAL_NOT_CLOSED",
]


def event(
    event_id: str,
    minute: int,
    actor_kind: str,
    actor_id: str,
    action: str,
    *,
    wake_id: str | None = None,
    scope: dict | None = None,
    data: dict | None = None,
) -> dict:
    return {
        "event_id": event_id,
        "minute": minute,
        "actor_kind": actor_kind,
        "actor_id": actor_id,
        "action": action,
        "run_id": "RUN-001",
        "wake_id": wake_id,
        "scope": scope,
        "data": data or {},
    }


def wake_scope(round_id: str = "R01") -> dict:
    return {
        "go_id": "GO-01-A",
        "cell_id": "CELL-01-A.01",
        "cell_ordinal": 1,
        "required_cell_total": 1,
        "round_id": round_id,
        "required_set_version": "REQ-001",
    }


def patrol_status_data(
    status: str,
    *,
    cycle_id: str = "PATROL-CYCLE-001",
    finding_ids: list[str] | None = None,
) -> dict:
    return {
        "cycle_id": cycle_id,
        "status": status,
        "checks": PATROL_CHECKS,
        "finding_ids": finding_ids or [],
        "evidence_refs": ["PATROL-SNAPSHOT-001"],
    }


def patrol_alert_data(
    finding_id: str,
    finding: str,
    observation_ref: str,
    *,
    cycle_id: str = "PATROL-CYCLE-001",
) -> dict:
    return {
        "cycle_id": cycle_id,
        "finding_id": finding_id,
        "finding": finding,
        "observation_refs": [observation_ref],
        "evidence_refs": [f"EVIDENCE::{observation_ref}"],
    }


def wake_attempt(
    level: int,
    minute: int,
    result: str,
    *,
    message: str = "GO-01-A CELL 1/1 已交付，请检查",
    target_host_id: str = "HOST-001",
    extra: dict | None = None,
) -> dict:
    data = {
        "level": level,
        "result": result,
        "signal": "DELIVERY",
        "target_thread_id": "THREAD-CHECKER-A",
        "target_host_id": target_host_id,
        "progress_identity": "RUN-001|REQ-001|GO-01-A|CELL-01-A.01|R01",
        "dispatch_event_id": "EVENT-DISPATCH-A",
        "message": message,
        "guessed_id": False,
        "created_replacement_checker": False,
    }
    if extra:
        data.update(extra)
    return event(
        f"EVENT-WAKE-L{level}",
        minute,
        "WORKER",
        "WORKER-A",
        "WAKE_ATTEMPT",
        wake_id="WAKE-001",
        scope=wake_scope(),
        data=data,
    )


def valid_trace() -> dict:
    return {
        "trace_type": "CLK_RUN_CONTROL_TRACE",
        "version": "2.6.0",
        "clock_mode": "INJECTED_MINUTES",
        "run": {
            "run_id": "RUN-001",
            "baseline_id": "BASELINE-001",
            "required_set_version": "REQ-001",
            "state": "RUNNING",
            "dispatch_phase": "ACTIVE",
            "pause_reason": None,
            "terminal_confirmed": False,
            "total_level_count": 1,
            "logical_active_go_limit": 2,
        },
        "required_sets": [
            {
                "version": "REQ-001",
                "baseline_id": "BASELINE-001",
                "level_id": "LEVEL-01",
                "required_go_ids": ["GO-01-A", "GO-01-B"],
                "required_cells": [
                    {"go_id": "GO-01-A", "cell_ids": ["CELL-01-A.01"]},
                    {"go_id": "GO-01-B", "cell_ids": ["CELL-01-B.01"]},
                ],
            }
        ],
        "device_capacity_profile": {
            "version": "DEVICE-001",
            "source": "MEASURED_OR_CONSERVATIVE",
            "cpu_model": "Example 8-core CPU",
            "logical_cores": 8,
            "available_ram_mb": 16384,
            "gpu_applicable": False,
            "gpu_model": None,
            "available_vram_mb": None,
            "disk_free_mb": 100000,
            "disk_io_mbps": 500,
            "network_mode": "RESTRICTED",
            "external_service_limit": 2,
            "allowed_processes": ["python"],
            "allowed_ports": [8000],
            "safe_command_concurrency": 1,
            "max_cell_wall_seconds": 1200,
            "max_single_command_seconds": 600,
            "context_budget_tokens": 100000,
            "evidence_budget_mb": 1000,
            "unknown_capabilities": [],
        },
        "engineering_load_snapshots": [
            {
                "version": "LOAD-001",
                "boundary": "RUN_FREEZE",
                "codebase_file_count": 100,
                "dependency_count": 10,
                "artifact_mb": 100,
                "full_regression_seconds": 100,
                "peak_ram_mb": 2000,
                "evidence_mb": 100,
                "hash_artifact_count": 20,
                "context_tokens": 10000,
                "context_reload_seconds": 30,
                "external_service_calls": 0,
                "cumulative_coupling_points": 10,
            }
        ],
        "cell_capacity_gates": [
            {
                "gate_id": "CAPACITY-GATE-001",
                "evaluated_minute": 0,
                "plan_version": "PLAN-001",
                "capacity_profile_version": "DEVICE-001",
                "load_snapshot_version": "LOAD-001",
                "go_id": "GO-01-A",
                "cell_id": "CELL-01-A.01",
                "implementation_scope": "Implement one bounded change.",
                "inputs": ["frozen contract"],
                "dependencies": [],
                "expected_artifacts": ["candidate artifact"],
                "build_test_matrix": ["focused tests"],
                "checker_verification": ["independent focused test"],
                "regression_scope": ["current GO"],
                "evidence_hash_cleanup": ["evidence", "hash", "cleanup"],
                "context_load": ["contract", "affected files"],
                "external_tools": [],
                "rollback_retry": ["restore checkpoint", "one retry budget"],
                "cumulative_coupling": ["accepted baseline"],
                "splittable": True,
                "go_outcome_hash": "a" * 64,
                "acceptance_hash": "b" * 64,
                "cost": {
                    "implementation_seconds": 200,
                    "build_seconds": 100,
                    "focused_test_seconds": 100,
                    "checker_seconds": 100,
                    "evidence_hash_cleanup_seconds": 50,
                    "rollback_retry_seconds": 50,
                    "external_tool_seconds": 0,
                    "implementation_peak_ram_mb": 3000,
                    "generated_artifact_mb": 100,
                    "context_tokens": 10000,
                    "evidence_mb": 50,
                    "concurrency_units": 1,
                    "max_single_command_seconds": 300,
                },
                "result": "PASS",
                "split": None,
            }
        ],
        "method_role_capabilities": [
            {"role_id": "SUPERVISOR-001", "role_kind": "SUPERVISOR", "set_thread_pinned": False},
            {"role_id": "CHECKER-A", "role_kind": "CHECKER", "set_thread_pinned": False},
            {"role_id": "WORKER-A", "role_kind": "WORKER", "set_thread_pinned": False},
            {"role_id": "VERIFICATION-D2-A", "role_kind": "VERIFICATION", "set_thread_pinned": False},
        ],
        "pin_observations": [],
        "worker_bindings": [
            {
                "worker_id": "WORKER-A",
                "role": "WORKER",
                "checker_id": "CHECKER-A",
                "checker_thread_id": "THREAD-CHECKER-A",
                "checker_host_id": "HOST-001",
                "checker_registry_ref": "ROLE-BINDING-CHECKER-A",
                "chain_id": "CHAIN-A",
                "capabilities": {
                    "send_message_to_thread": True,
                    "read_thread": True,
                    "list_threads": True,
                    "unarchive_thread": True,
                    "temporary_heartbeat_upsert_delete": True,
                    "pending_wake_write": True,
                },
            }
        ],
        "patrols": [
            {
                "patrol_id": "PATROL-RUN-001",
                "conversation_type": "RUN_PATROL_CONVERSATION",
                "conversation_id": "CONVERSATION-PATROL-001",
                "thread_id": "THREAD-PATROL-001",
                "host_id": "HOST-001",
                "visible": True,
                "authoritative": False,
                "technical_acceptance": False,
                "product_work": False,
                "set_thread_pinned": False,
                "model_binding_id": "BINDING::PATROL-RUN-001::001",
                "model": "gpt-5.6-terra",
                "reasoning_effort": "xhigh",
                "project_workload": "MEDIUM",
                "interval_minutes": 15,
                "heartbeat_id": "PATROL::RUN-001",
                "heartbeat_count": 1,
                "heartbeat_state": "ACTIVE",
            }
        ],
        "events": [
            event(
                "EVENT-DISPATCH-A",
                0,
                "CHECKER",
                "CHECKER-A",
                "CELL_DISPATCH",
                wake_id="WAKE-001",
                scope=wake_scope(),
                data={
                    "gate_id": "CAPACITY-GATE-001",
                    "plan_version": "PLAN-001",
                    "worker_id": "WORKER-A",
                    "checker_id": "CHECKER-A",
                },
            ),
            wake_attempt(1, 0, "SENT"),
            event(
                "EVENT-ACK",
                1,
                "CHECKER",
                "CHECKER-A",
                "WAKE_ACK",
                wake_id="WAKE-001",
                scope=wake_scope(),
            ),
            event(
                "EVENT-CHECK-START",
                1,
                "CHECKER",
                "CHECKER-A",
                "CHECKER_START",
                wake_id="WAKE-001",
                scope=wake_scope(),
                data={"message": "收到 GO-01-A CELL 1/1，开始检查"},
            ),
            event(
                "EVENT-PROGRESS-DELIVERED",
                1,
                "CHECKER",
                "CHECKER-A",
                "CHECKER_PROGRESS",
                scope=wake_scope(),
                data={
                    "trigger_event_id": "EVENT-ACK",
                    "trigger_receipt_id": None,
                    "accepted_cell_count": 0,
                    "required_cell_total": 1,
                    "state": "DELIVERED",
                },
            ),
            event(
                "EVENT-D1-A",
                2,
                "CHECKER",
                "CHECKER-A",
                "D1_VERDICT",
                scope=wake_scope(),
                data={
                    "receipt_id": "RECEIPT-D1-A",
                    "result": "PASS",
                    "effective": True,
                    "required_set_version": "REQ-001",
                },
            ),
            event(
                "EVENT-PROGRESS-D1",
                2,
                "CHECKER",
                "CHECKER-A",
                "CHECKER_PROGRESS",
                scope=wake_scope(),
                data={
                    "trigger_event_id": "EVENT-D1-A",
                    "trigger_receipt_id": "RECEIPT-D1-A",
                    "accepted_cell_count": 1,
                    "required_cell_total": 1,
                    "state": "D1_ACCEPTED",
                    "next_state": "GO_CANDIDATE_READY",
                },
            ),
            event(
                "EVENT-CANDIDATE-A",
                2,
                "CHECKER",
                "CHECKER-A",
                "GO_MILESTONE",
                scope=wake_scope(),
                data={
                    "go_ordinal": 1,
                    "required_go_total": 2,
                    "accepted_cell_count": 1,
                    "required_cell_total": 1,
                    "status": "GO_CANDIDATE_READY",
                },
            ),
            event(
                "EVENT-SUPERVISOR-CANDIDATE",
                2,
                "SUPERVISOR",
                "SUPERVISOR-001",
                "SUPERVISOR_PROGRESS",
                data={
                    "trigger_event_id": "EVENT-CANDIDATE-A",
                    "required_set_version": "REQ-001",
                    "current_level_verified_go_count": 0,
                    "current_level_required_go_total": 2,
                    "completed_level_count": 0,
                    "total_level_count": 1,
                    "state": "GO_CANDIDATE_READY",
                },
            ),
            event(
                "EVENT-D2-A",
                3,
                "VERIFICATION",
                "VERIFICATION-D2-A",
                "D2_VERDICT",
                scope={"go_id": "GO-01-A"},
                data={
                    "verdict_id": "VERDICT-D2-A",
                    "result": "GO_VERIFIED",
                    "required_set_version": "REQ-001",
                },
            ),
            event(
                "EVENT-SUPERVISOR-D2",
                3,
                "SUPERVISOR",
                "SUPERVISOR-001",
                "SUPERVISOR_PROGRESS",
                data={
                    "trigger_event_id": "EVENT-D2-A",
                    "required_set_version": "REQ-001",
                    "current_level_verified_go_count": 1,
                    "current_level_required_go_total": 2,
                    "completed_level_count": 0,
                    "total_level_count": 1,
                    "state": "D2_VERIFIED",
                },
            ),
        ],
    }


def write_trace(tmp_path: Path, trace: dict, name: str = "trace.yaml") -> Path:
    path = tmp_path / name
    path.write_text(
        yaml.safe_dump(trace, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    return path


def run_trace(path: Path, *, optimized: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable]
    if optimized:
        command.append("-O")
    command.extend([str(VALIDATOR), str(path)])
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def assert_valid(tmp_path: Path, trace: dict) -> None:
    result = run_trace(write_trace(tmp_path, trace))
    assert result.returncode == 0, result.stderr
    assert "PASS: CLK run control trace" in result.stdout


def assert_invalid(tmp_path: Path, trace: dict, message: str) -> None:
    result = run_trace(write_trace(tmp_path, trace))
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert message in result.stderr


def replace_wake_events(trace: dict, replacement: list[dict]) -> None:
    trace["events"] = [
        item
        for item in trace["events"]
        if item["action"] not in {"WAKE_ATTEMPT", "WAKE_ACK", "CHECKER_START"}
    ]
    trace["events"] = replacement + trace["events"]
    trace["events"].sort(key=lambda item: item["minute"])


def level2_success_trace(*, repaired_host: bool = False) -> dict:
    trace = valid_trace()
    level2_extra = {
        "inspected_original_thread": True,
        "resolved_checker_id": "CHECKER-A",
        "resolved_from_frozen_registry": True,
        "observed_archived": repaired_host,
        "unarchived_original": repaired_host,
        "observed_host_mismatch": repaired_host,
    }
    replacement = [
        wake_attempt(1, 0, "FAILED"),
        wake_attempt(
            2,
            2,
            "SENT",
            target_host_id="HOST-002" if repaired_host else "HOST-001",
            extra=level2_extra,
        ),
        event(
            "EVENT-ACK",
            3,
            "CHECKER",
            "CHECKER-A",
            "WAKE_ACK",
            wake_id="WAKE-001",
            scope=wake_scope(),
        ),
        event(
            "EVENT-CHECK-START",
            3,
            "CHECKER",
            "CHECKER-A",
            "CHECKER_START",
            wake_id="WAKE-001",
            scope=wake_scope(),
            data={"message": "收到 GO-01-A CELL 1/1，开始检查"},
        ),
    ]
    replace_wake_events(trace, replacement)
    for item in trace["events"]:
        if item["event_id"] not in {event["event_id"] for event in replacement} and item["action"] != "CELL_DISPATCH":
            item["minute"] += 2
    trace["events"].sort(key=lambda item: item["minute"])
    return trace


def level3_success_trace() -> dict:
    trace = valid_trace()
    heartbeat_id = "WAKE::RUN-001::CHECKER-A::GO-01-A::CELL-01-A.01::R01"
    replacement = [
        wake_attempt(1, 0, "FAILED"),
        wake_attempt(
            2,
            2,
            "FAILED",
            extra={
                "inspected_original_thread": True,
                "resolved_checker_id": "CHECKER-A",
                "resolved_from_frozen_registry": True,
                "observed_archived": False,
                "unarchived_original": False,
                "observed_host_mismatch": False,
            },
        ),
        wake_attempt(3, 4, "SENT", extra={"temporary_heartbeat_id": heartbeat_id}),
        event(
            "EVENT-TEMP-HEARTBEAT",
            4,
            "WORKER",
            "WORKER-A",
            "TEMP_HEARTBEAT_UPSERT",
            wake_id="WAKE-001",
            scope=wake_scope(),
            data={"heartbeat_id": heartbeat_id, "unique_count": 1},
        ),
        event(
            "EVENT-ACK",
            5,
            "CHECKER",
            "CHECKER-A",
            "WAKE_ACK",
            wake_id="WAKE-001",
            scope=wake_scope(),
        ),
        event(
            "EVENT-TEMP-HEARTBEAT-DELETE",
            5,
            "CHECKER",
            "CHECKER-A",
            "TEMP_HEARTBEAT_DELETE",
            wake_id="WAKE-001",
            scope=wake_scope(),
            data={"heartbeat_id": heartbeat_id},
        ),
        event(
            "EVENT-CHECK-START",
            5,
            "CHECKER",
            "CHECKER-A",
            "CHECKER_START",
            wake_id="WAKE-001",
            scope=wake_scope(),
            data={"message": "收到 GO-01-A CELL 1/1，开始检查"},
        ),
    ]
    replace_wake_events(trace, replacement)
    for item in trace["events"]:
        if item["event_id"] not in {event["event_id"] for event in replacement} and item["action"] != "CELL_DISPATCH":
            item["minute"] += 4
    trace["events"].sort(key=lambda item: item["minute"])
    return trace


def pending_wake_trace() -> dict:
    trace = level3_success_trace()
    trace["events"] = [
        item
        for item in trace["events"]
        if item["action"]
        not in {
            "WAKE_ACK",
            "TEMP_HEARTBEAT_DELETE",
            "CHECKER_START",
            "CHECKER_PROGRESS",
            "D1_VERDICT",
            "GO_MILESTONE",
            "SUPERVISOR_PROGRESS",
            "D2_VERDICT",
        }
    ]
    level3 = next(item for item in trace["events"] if item["action"] == "WAKE_ATTEMPT" and item["data"]["level"] == 3)
    level3["data"]["result"] = "FAILED"
    trace["events"].extend(
        [
            event(
                "EVENT-PENDING-WAKE",
                6,
                "WORKER",
                "WORKER-A",
                "PENDING_WAKE_WRITE",
                wake_id="WAKE-001",
                scope=wake_scope(),
                data={
                    "progress_identity": "RUN-001|REQ-001|GO-01-A|CELL-01-A.01|R01",
                    "message": "GO-01-A CELL 1/1 已交付，请检查",
                    "attempt_levels": [1, 2, 3],
                    "errors": ["send failed", "thread not found", "heartbeat unacknowledged"],
                },
            ),
            event(
                "EVENT-PENDING-CONSUME",
                7,
                "PATROL",
                "PATROL-RUN-001",
                "PENDING_WAKE_CONSUME",
                wake_id="WAKE-001",
                scope=wake_scope(),
                data={"pending_event_id": "EVENT-PENDING-WAKE"},
            ),
            event(
                "EVENT-PATROL-ALERT",
                7,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_ALERT",
                wake_id="WAKE-001",
                data=patrol_alert_data(
                    "FINDING-PENDING-WAKE",
                    "PENDING_WAKE",
                    "EVENT-PENDING-WAKE",
                ),
            ),
            event(
                "EVENT-PATROL-STATUS",
                7,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_STATUS",
                data=patrol_status_data(
                    "ALERTS_EMITTED",
                    finding_ids=["FINDING-PENDING-WAKE"],
                ),
            ),
        ]
    )
    trace["events"].sort(key=lambda item: item["minute"])
    return trace


def test_level1_success_stops_escalation(tmp_path: Path) -> None:
    assert_valid(tmp_path, valid_trace())


def test_level1_failure_then_level2_success(tmp_path: Path) -> None:
    assert_valid(tmp_path, level2_success_trace())


def test_level2_repairs_archive_and_host_for_same_checker(tmp_path: Path) -> None:
    assert_valid(tmp_path, level2_success_trace(repaired_host=True))


def test_thread_not_found_cannot_guess_or_create_replacement(tmp_path: Path) -> None:
    trace = pending_wake_trace()
    level2 = next(item for item in trace["events"] if item["action"] == "WAKE_ATTEMPT" and item["data"]["level"] == 2)
    level2["data"]["result"] = "THREAD_NOT_FOUND"
    assert_valid(tmp_path, trace)
    level2["data"]["guessed_id"] = True
    assert_invalid(tmp_path, trace, "must not guess")


def test_level3_heartbeat_is_unique_and_deleted_after_ack(tmp_path: Path) -> None:
    assert_valid(tmp_path, level3_success_trace())


def test_three_failures_create_pending_wake_consumed_by_unique_patrol(tmp_path: Path) -> None:
    assert_valid(tmp_path, pending_wake_trace())


def test_ack_immediately_stops_higher_levels(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(wake_attempt(2, 2, "SENT"))
    trace["events"].sort(key=lambda item: item["minute"])
    assert_invalid(tmp_path, trace, "after wake success")


def test_non_worker_cannot_use_wake_ladder(tmp_path: Path) -> None:
    trace = valid_trace()
    next(item for item in trace["events"] if item["action"] == "WAKE_ATTEMPT")["actor_kind"] = "CHECKER"
    assert_invalid(tmp_path, trace, "only WORKER")


def test_dispatched_cell_cannot_omit_its_complete_wake_lifecycle(tmp_path: Path) -> None:
    trace = valid_trace()
    wake_actions = {
        "WAKE_ATTEMPT", "WAKE_ACK", "MECHANICAL_CHECKER_STARTED", "CHECKER_START",
        "TEMP_HEARTBEAT_UPSERT", "TEMP_HEARTBEAT_DELETE", "PENDING_WAKE_WRITE",
        "PENDING_WAKE_CONSUME",
    }
    trace["events"] = [item for item in trace["events"] if item["action"] not in wake_actions]
    assert_invalid(tmp_path, trace, "CELL dispatch requires one wake lifecycle")


def test_active_trace_cannot_erase_all_events(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"] = []
    assert_invalid(tmp_path, trace, "ACTIVE dispatch phase requires CELL_DISPATCH")


def test_worker_wake_lifecycle_cannot_exist_without_its_dispatch(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"] = [item for item in trace["events"] if item["action"] != "CELL_DISPATCH"]
    assert_invalid(tmp_path, trace, "wake lifecycle requires one CELL_DISPATCH")


def test_initial_undispatched_trace_allows_no_wake_but_rejects_worker_signal(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["run"]["dispatch_phase"] = "INITIAL_UNDISPATCHED"
    trace["events"] = []
    assert_valid(tmp_path, trace)
    trace["events"].append(
        event(
            "EVENT-ORPHAN-SCOPE-EXCEEDED",
            0,
            "WORKER",
            "WORKER-A",
            "CELL_SCOPE_EXCEEDED",
            scope=wake_scope(),
            data={
                "checkpoint_id": "CHECKPOINT-ORPHAN",
                "evidence_hash": "d" * 64,
                "worker_continued": False,
            },
        )
    )
    assert_invalid(tmp_path, trace, "INITIAL_UNDISPATCHED trace cannot contain Worker signal")


def test_supervisor_wait_threads_is_rejected_but_zero_snapshot_is_allowed(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(
        event(
            "EVENT-SNAPSHOT",
            4,
            "SUPERVISOR",
            "SUPERVISOR-001",
            "READ_THREAD_SNAPSHOT",
            data={"timeout_ms": 0},
        )
    )
    assert_valid(tmp_path, trace)
    trace["events"][-1]["action"] = "WAIT_THREADS"
    assert_invalid(tmp_path, trace, "Supervisor wait_threads")


def test_visible_task_and_subtask_text_are_not_subagents(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].extend(
        [
            event(
                "EVENT-VISIBLE-TASK",
                4,
                "SYSTEM",
                "CODEX",
                "OBSERVE_VISIBLE_TASK",
                data={"thread_id": "THREAD-CHECKER-A", "visible": True, "stable_thread_id": True},
            ),
            event(
                "EVENT-SUBTASK-TERM",
                4,
                "SYSTEM",
                "CODEX",
                "TERM_CLASSIFICATION",
                data={"text": "子任务：执行 GO-01-A/CELL-01-A.01/R01", "classification": "SUBTASK"},
            ),
        ]
    )
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize(
    "action",
    ["OBSERVE_SPAWN_AGENT", "OBSERVE_DELEGATE_TASK", "OBSERVE_HIDDEN_AGENT", "OBSERVE_BACKGROUND_AGENT"],
)
def test_subagent_capability_evidence_is_rejected(tmp_path: Path, action: str) -> None:
    trace = valid_trace()
    trace["events"].append(event("EVENT-FORBIDDEN-AGENT", 4, "SYSTEM", "CODEX", action))
    assert_invalid(tmp_path, trace, "subagent capability evidence")


def test_formal_pause_is_not_false_alerted(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["run"].update(
        state="PAUSED", pause_reason="FORMAL_PAUSE", dispatch_phase="INITIAL_UNDISPATCHED"
    )
    trace["events"] = [
        event(
            "EVENT-PAUSE-STATUS",
            0,
            "PATROL",
            "PATROL-RUN-001",
            "PATROL_STATUS",
            data=patrol_status_data("LEGAL_PAUSE"),
        )
    ]
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize(
    ("run_state", "patrol_status"),
    [("BLOCKED", "LEGAL_BLOCKED"), ("WAITING_EXTERNAL", "LEGAL_EXTERNAL_WAIT")],
)
def test_legal_blocked_and_external_wait_are_not_false_alerted(
    tmp_path: Path, run_state: str, patrol_status: str
) -> None:
    trace = valid_trace()
    trace["run"].update(
        state=run_state,
        pause_reason="AUTHORIZED_CONDITION",
        dispatch_phase="INITIAL_UNDISPATCHED",
    )
    trace["events"] = [
        event(
            "EVENT-LEGAL-STATUS",
            0,
            "PATROL",
            "PATROL-RUN-001",
            "PATROL_STATUS",
            data=patrol_status_data(patrol_status),
        )
    ]
    assert_valid(tmp_path, trace)


def test_unexplained_stall_uses_fixed_bound_patrol_finding(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].extend(
        [
            event(
                "EVENT-STALL-ALERT",
                4,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_ALERT",
                data=patrol_alert_data(
                    "FINDING-STALL",
                    "UNEXPLAINED_STALL",
                    "STALL-OBSERVATION-001",
                ),
            ),
            event(
                "EVENT-STALL-STATUS",
                4,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_STATUS",
                data=patrol_status_data(
                    "ALERTS_EMITTED", finding_ids=["FINDING-STALL"]
                ),
            ),
        ]
    )
    assert_valid(tmp_path, trace)


def test_patrol_status_rejects_free_text_without_fixed_checks_or_evidence(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(
        event(
            "EVENT-ARBITRARY-PATROL",
            4,
            "PATROL",
            "PATROL-RUN-001",
            "PATROL_STATUS",
            data={"reason": "EVERYTHING_FINE_WITHOUT_CHECKS"},
        )
    )
    assert_invalid(tmp_path, trace, "patrol status must bind the complete mechanical check set")


def test_duplicate_patrol_or_heartbeat_is_rejected(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["patrols"].append(deepcopy(trace["patrols"][0]))
    assert_invalid(tmp_path, trace, "patrol")


def test_terminal_cleanup_deletes_heartbeat_closes_and_archives(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["run"].update(
        state="LOOP_TERMINAL", terminal_confirmed=True, dispatch_phase="TERMINAL"
    )
    trace["patrols"][0]["heartbeat_state"] = "DELETED"
    trace["events"] = [
        event("EVENT-TERMINAL", 0, "SUPERVISOR", "SUPERVISOR-001", "LOOP_TERMINAL_CONFIRMED"),
        event("EVENT-PATROL-HB-DELETE", 0, "PATROL", "PATROL-RUN-001", "PATROL_HEARTBEAT_DELETE"),
        event("EVENT-PATROL-CLOSED", 0, "PATROL", "PATROL-RUN-001", "PATROL_CLOSED"),
        event("EVENT-PATROL-ARCHIVE", 0, "PATROL", "PATROL-RUN-001", "PATROL_ARCHIVE"),
    ]
    assert_valid(tmp_path, trace)
    trace["events"].pop()
    assert_invalid(tmp_path, trace, "terminal patrol sequence")


def test_missing_worker_capability_fails_closed(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["worker_bindings"][0]["capabilities"]["pending_wake_write"] = False
    assert_invalid(tmp_path, trace, "capability preflight")


def test_worker_signal_requires_scope_position_and_delivery_semantics(tmp_path: Path) -> None:
    trace = valid_trace()
    next(item for item in trace["events"] if item["action"] == "WAKE_ATTEMPT")["data"]["message"] = "完成，请检验"
    assert_invalid(tmp_path, trace, "scoped Worker message")


def test_all_wake_levels_keep_one_progress_identity(tmp_path: Path) -> None:
    trace = level2_success_trace()
    level2 = next(item for item in trace["events"] if item["action"] == "WAKE_ATTEMPT" and item["data"]["level"] == 2)
    level2["data"]["progress_identity"] += "-DRIFT"
    assert_invalid(tmp_path, trace, "same progress identity")


def test_delivery_does_not_increase_d1_accepted_count(tmp_path: Path) -> None:
    trace = valid_trace()
    first_progress = next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-DELIVERED")
    first_progress["data"]["accepted_cell_count"] = 1
    assert_invalid(tmp_path, trace, "accepted CELL count")


def test_effective_d1_pass_increments_once_and_duplicate_receipt_does_not(tmp_path: Path) -> None:
    trace = valid_trace()
    duplicate = deepcopy(next(item for item in trace["events"] if item["event_id"] == "EVENT-D1-A"))
    duplicate["event_id"] = "EVENT-D1-A-DUPLICATE"
    trace["events"].insert(trace["events"].index(next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-D1")), duplicate)
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize("result", ["FAIL", "BLOCKED"])
def test_rework_or_blocked_d1_does_not_increment(tmp_path: Path, result: str) -> None:
    trace = valid_trace()
    d1 = next(item for item in trace["events"] if item["event_id"] == "EVENT-D1-A")
    d1["data"]["result"] = result
    trace["events"] = [
        item
        for item in trace["events"]
        if item["action"] not in {"GO_MILESTONE", "SUPERVISOR_PROGRESS", "D2_VERDICT"}
        or item["event_id"] == "EVENT-PROGRESS-DELIVERED"
    ]
    progress = next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-D1")
    progress["data"].update(
        accepted_cell_count=0,
        state="DELIVERED",
        next_state="REWORK" if result == "FAIL" else "BLOCKED",
    )
    assert_valid(tmp_path, trace)


def test_go_candidate_ready_is_not_d2_verified(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"] = [item for item in trace["events"] if item["event_id"] not in {"EVENT-D2-A", "EVENT-SUPERVISOR-D2"}]
    assert_valid(tmp_path, trace)
    candidate_update = next(item for item in trace["events"] if item["event_id"] == "EVENT-SUPERVISOR-CANDIDATE")
    candidate_update["data"].update(current_level_verified_go_count=1, state="D2_VERIFIED")
    assert_invalid(tmp_path, trace, "D2 verified GO count")


def test_checker_milestone_is_only_allowed_at_go_boundary(tmp_path: Path) -> None:
    trace = valid_trace()
    milestone = next(item for item in trace["events"] if item["action"] == "GO_MILESTONE")
    milestone["minute"] = 1
    trace["events"].remove(milestone)
    trace["events"].insert(4, milestone)
    assert_invalid(tmp_path, trace, "GO milestone requires all Required CELLs")


def test_supervisor_progress_uses_current_level_topology_and_verdicts(tmp_path: Path) -> None:
    trace = valid_trace()
    update = next(item for item in trace["events"] if item["event_id"] == "EVENT-SUPERVISOR-D2")
    update["data"]["current_level_verified_go_count"] = 2
    assert_invalid(tmp_path, trace, "D2 verified GO count")


def test_every_d1_verdict_requires_exactly_one_bound_checker_progress(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"] = [item for item in trace["events"] if item["event_id"] != "EVENT-PROGRESS-D1"]
    assert_invalid(tmp_path, trace, "D1 verdict requires exactly one Checker progress update")


def test_checker_progress_rejects_wrong_order_and_wrong_trigger(tmp_path: Path) -> None:
    trace = valid_trace()
    progress = next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-D1")
    progress["minute"] = 1
    trace["events"].sort(key=lambda item: item["minute"])
    assert_invalid(tmp_path, trace, "Checker progress cannot precede its D1 verdict")

    trace = valid_trace()
    progress = next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-D1")
    progress["data"].update(trigger_event_id="EVENT-ACK", trigger_receipt_id=None)
    assert_invalid(tmp_path, trace, "D1 verdict requires exactly one Checker progress update")

    trace = valid_trace()
    duplicate = deepcopy(next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-D1"))
    duplicate["event_id"] = "EVENT-PROGRESS-D1-DUPLICATE"
    trace["events"].append(duplicate)
    trace["events"].sort(key=lambda item: item["minute"])
    assert_invalid(tmp_path, trace, "D1 verdict requires exactly one Checker progress update")


def test_every_material_trigger_requires_exactly_one_supervisor_progress(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"] = [item for item in trace["events"] if item["action"] != "SUPERVISOR_PROGRESS"]
    assert_invalid(tmp_path, trace, "material progress trigger requires exactly one Supervisor progress update")

    trace = valid_trace()
    duplicate = deepcopy(next(item for item in trace["events"] if item["event_id"] == "EVENT-SUPERVISOR-D2"))
    duplicate["event_id"] = "EVENT-SUPERVISOR-D2-DUPLICATE"
    trace["events"].append(duplicate)
    trace["events"].sort(key=lambda item: item["minute"])
    assert_invalid(tmp_path, trace, "material progress trigger requires exactly one Supervisor progress update")


def test_supervisor_progress_cannot_let_one_trigger_cover_another(tmp_path: Path) -> None:
    trace = valid_trace()
    candidate = next(item for item in trace["events"] if item["event_id"] == "EVENT-SUPERVISOR-CANDIDATE")
    candidate["data"]["trigger_event_id"] = "EVENT-D2-A"
    assert_invalid(tmp_path, trace, "material progress trigger requires exactly one Supervisor progress update")


def test_required_set_amendment_recomputes_denominator(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["required_sets"].append(
        {
            "version": "REQ-002",
            "baseline_id": "BASELINE-002",
            "level_id": "LEVEL-01",
            "required_go_ids": ["GO-01-A"],
            "required_cells": [{"go_id": "GO-01-A", "cell_ids": ["CELL-01-A.01"]}],
        }
    )
    trace["events"].extend(
        [
            event(
                "EVENT-AMEND",
                4,
                "SUPERVISOR",
                "SUPERVISOR-001",
                "REQUIRED_SET_AMENDMENT",
                data={
                    "source_type": "MANIFEST",
                    "new_required_set_version": "REQ-002",
                    "preserved_d1_receipt_ids": ["RECEIPT-D1-A"],
                    "preserved_d2_verdict_ids": ["VERDICT-D2-A"],
                },
            ),
            event(
                "EVENT-SUPERVISOR-AMEND",
                4,
                "SUPERVISOR",
                "SUPERVISOR-001",
                "SUPERVISOR_PROGRESS",
                data={
                    "trigger_event_id": "EVENT-AMEND",
                    "required_set_version": "REQ-002",
                    "current_level_verified_go_count": 1,
                    "current_level_required_go_total": 1,
                    "completed_level_count": 0,
                    "total_level_count": 1,
                    "state": "D2_VERIFIED",
                },
            ),
        ]
    )
    assert_valid(tmp_path, trace)


def test_supervisor_does_not_rebroadcast_worker_cell_noise(tmp_path: Path) -> None:
    trace = valid_trace()
    noisy = event(
        "EVENT-SUPERVISOR-NOISE",
        1,
        "SUPERVISOR",
        "SUPERVISOR-001",
        "SUPERVISOR_PROGRESS",
        data={
            "trigger_event_id": "EVENT-WAKE-L1",
            "required_set_version": "REQ-001",
            "current_level_verified_go_count": 0,
            "current_level_required_go_total": 2,
            "completed_level_count": 0,
            "total_level_count": 1,
            "state": "DELIVERED",
        },
    )
    trace["events"].insert(3, noisy)
    assert_invalid(tmp_path, trace, "Supervisor progress trigger")


def add_late_split_gate(trace: dict, *, successor_count: int = 2) -> dict:
    late_load = deepcopy(trace["engineering_load_snapshots"][0])
    late_load.update(
        version="LOAD-002",
        boundary="LEVEL_BOUNDARY",
        full_regression_seconds=1000,
        peak_ram_mb=4000,
        evidence_mb=200,
        context_tokens=20000,
        context_reload_seconds=100,
        cumulative_coupling_points=80,
    )
    trace["engineering_load_snapshots"].append(late_load)
    gate = deepcopy(trace["cell_capacity_gates"][0])
    gate.update(
        gate_id="CAPACITY-GATE-LATE",
        evaluated_minute=4,
        load_snapshot_version="LOAD-002",
        cell_id="CELL-01-A.02",
        result="SPLIT_REQUIRED",
    )
    gate["split"] = {
        "pre_dispatch": True,
        "go_outcome_hash": gate["go_outcome_hash"],
        "acceptance_hash": gate["acceptance_hash"],
        "successor_cells": [
            {
                "cell_id": f"CELL-01-A.02-{index}",
                "independently_deliverable": True,
                "independently_d1_checkable": True,
                "dependencies": [] if index == 1 else [f"CELL-01-A.02-{index - 1}"],
            }
            for index in range(1, successor_count + 1)
        ],
    }
    trace["cell_capacity_gates"].append(gate)
    return gate


def test_same_small_surface_passes_early_and_requires_split_after_load_growth(tmp_path: Path) -> None:
    trace = valid_trace()
    add_late_split_gate(trace)
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize(
    ("field", "value"),
    [("available_ram_mb", 1000), ("disk_free_mb", 50), ("safe_command_concurrency", 0)],
)
def test_low_device_capacity_rejects_heavy_cell(tmp_path: Path, field: str, value: int) -> None:
    trace = valid_trace()
    trace["device_capacity_profile"][field] = value
    assert_invalid(tmp_path, trace, "capacity gate result")


def test_unknown_device_capability_is_capacity_blocked(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["device_capacity_profile"]["unknown_capabilities"] = ["AVAILABLE_RAM"]
    trace["cell_capacity_gates"][0]["result"] = "CAPACITY_BLOCKED"
    trace["run"]["dispatch_phase"] = "INITIAL_UNDISPATCHED"
    trace["events"] = []
    assert_valid(tmp_path, trace)
    trace["cell_capacity_gates"][0]["result"] = "PASS"
    assert_invalid(tmp_path, trace, "unknown capability")


def test_worker_dispatch_requires_current_capacity_pass(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["device_capacity_profile"]["available_ram_mb"] = 1000
    gate = trace["cell_capacity_gates"][0]
    gate["result"] = "SPLIT_REQUIRED"
    gate["split"] = {
        "pre_dispatch": True,
        "go_outcome_hash": gate["go_outcome_hash"],
        "acceptance_hash": gate["acceptance_hash"],
        "successor_cells": [
            {"cell_id": "CELL-01-A.01-1", "independently_deliverable": True, "independently_d1_checkable": True, "dependencies": []},
            {"cell_id": "CELL-01-A.01-2", "independently_deliverable": True, "independently_d1_checkable": True, "dependencies": ["CELL-01-A.01-1"]},
        ],
    }
    assert_invalid(tmp_path, trace, "dispatch requires current PASS")


def test_pre_dispatch_split_preserves_go_outcome_and_acceptance(tmp_path: Path) -> None:
    trace = valid_trace()
    gate = add_late_split_gate(trace)
    assert_valid(tmp_path, trace)
    gate["split"]["acceptance_hash"] = "c" * 64
    assert_invalid(tmp_path, trace, "preserve GO outcome and acceptance")


def test_worker_cannot_split_but_can_report_scope_exceeded_with_checkpoint(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(
        event(
            "EVENT-SCOPE-EXCEEDED",
            4,
            "WORKER",
            "WORKER-A",
            "CELL_SCOPE_EXCEEDED",
            scope=wake_scope(),
            data={
                "gate_id": "CAPACITY-GATE-001",
                "checkpoint_id": "CHECKPOINT-001",
                "evidence_hash": "d" * 64,
                "worker_continued": False,
            },
        )
    )
    assert_valid(tmp_path, trace)
    trace["events"][-1]["action"] = "CELL_SPLIT"
    assert_invalid(tmp_path, trace, "Worker must not split")


def post_dispatch_split_event(successor_count: int, *, severe: bool) -> dict:
    data = {
        "original_cell_id": "CELL-01-A.01",
        "successor_cell_ids": [f"CELL-01-A.01-{index}" for index in range(1, successor_count + 1)],
        "new_required_set_version": "REQ-POST-SPLIT",
        "planning_defect": "POST_DISPATCH_CELL_SPLIT",
        "severity": "CELL_OVERSIZE_SEVERE" if severe else None,
        "reassess_remaining_plan": severe,
        "reassess_device_profile": severe,
        "reassess_load_model": severe,
    }
    return event(
        "EVENT-POST-DISPATCH-SPLIT",
        4,
        "CHECKER",
        "CHECKER-A",
        "POST_DISPATCH_CELL_SPLIT",
        scope=wake_scope(),
        data=data,
    )


def test_post_dispatch_three_way_split_requires_severe_reassessment(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(post_dispatch_split_event(3, severe=True))
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize("successor_count", [3, 6, 7, 8])
def test_large_post_dispatch_split_without_severe_handling_is_rejected(
    tmp_path: Path, successor_count: int
) -> None:
    trace = valid_trace()
    trace["events"].append(post_dispatch_split_event(successor_count, severe=False))
    assert_invalid(tmp_path, trace, "CELL_OVERSIZE_SEVERE")


def test_actual_peak_feedback_requires_latest_load_for_future_gate(tmp_path: Path) -> None:
    trace = valid_trace()
    late_gate = add_late_split_gate(trace)
    trace["events"].append(
        event(
            "EVENT-LOAD-FEEDBACK",
            4,
            "SUPERVISOR",
            "SUPERVISOR-001",
            "LOAD_FEEDBACK",
            data={"new_load_snapshot_version": "LOAD-002"},
        )
    )
    late_gate["evaluated_minute"] = 5
    assert_valid(tmp_path, trace)
    late_gate["load_snapshot_version"] = "LOAD-001"
    assert_invalid(tmp_path, trace, "latest cumulative load")


def test_logical_level_parallelism_allows_lower_safe_device_concurrency(tmp_path: Path) -> None:
    trace = valid_trace()
    assert trace["run"]["logical_active_go_limit"] == 2
    assert trace["device_capacity_profile"]["safe_command_concurrency"] == 1
    assert_valid(tmp_path, trace)


def test_capacity_split_recomputes_progress_denominator_without_increment(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["device_capacity_profile"]["available_ram_mb"] = 1000
    trace["required_sets"].append(
        {
            "version": "REQ-SPLIT",
            "baseline_id": "BASELINE-001",
            "level_id": "LEVEL-01",
            "required_go_ids": ["GO-01-A", "GO-01-B"],
            "required_cells": [
                {"go_id": "GO-01-A", "cell_ids": ["CELL-01-A.01-1", "CELL-01-A.01-2"]},
                {"go_id": "GO-01-B", "cell_ids": ["CELL-01-B.01"]},
            ],
        }
    )
    trace["run"]["dispatch_phase"] = "INITIAL_UNDISPATCHED"
    trace["events"] = [
        event(
            "EVENT-PRE-SPLIT",
            0,
            "CHECKER",
            "CHECKER-A",
            "PRE_DISPATCH_CELL_SPLIT",
            scope=wake_scope(),
            data={
                "gate_id": "CAPACITY-GATE-001",
                "new_required_set_version": "REQ-SPLIT",
                "successor_cell_ids": ["CELL-01-A.01-1", "CELL-01-A.01-2"],
                "go_outcome_hash": "a" * 64,
                "acceptance_hash": "b" * 64,
            },
        ),
        event(
            "EVENT-SPLIT-AMEND",
            0,
            "SUPERVISOR",
            "SUPERVISOR-001",
            "REQUIRED_SET_AMENDMENT",
            data={
                "source_type": "CELL_CAPACITY_SPLIT",
                "new_required_set_version": "REQ-SPLIT",
                "preserved_d1_receipt_ids": [],
                "preserved_d2_verdict_ids": [],
            },
        ),
        event(
            "EVENT-SPLIT-PROGRESS",
            0,
            "CHECKER",
            "CHECKER-A",
            "CHECKER_PROGRESS",
            scope={**wake_scope(), "cell_id": "CELL-01-A.01-1", "required_cell_total": 2, "required_set_version": "REQ-SPLIT"},
            data={
                "trigger_event_id": "EVENT-SPLIT-AMEND",
                "trigger_receipt_id": None,
                "accepted_cell_count": 0,
                "required_cell_total": 2,
                "state": "DELIVERED",
            },
        ),
        event(
            "EVENT-SPLIT-SUPERVISOR-PROGRESS",
            0,
            "SUPERVISOR",
            "SUPERVISOR-001",
            "SUPERVISOR_PROGRESS",
            data={
                "trigger_event_id": "EVENT-SPLIT-AMEND",
                "required_set_version": "REQ-SPLIT",
                "current_level_verified_go_count": 0,
                "current_level_required_go_total": 2,
                "completed_level_count": 0,
                "total_level_count": 1,
                "state": "PLAN_REVISED",
            },
        ),
    ]
    gate = trace["cell_capacity_gates"][0]
    gate["result"] = "SPLIT_REQUIRED"
    gate["split"] = {
        "pre_dispatch": True,
        "go_outcome_hash": gate["go_outcome_hash"],
        "acceptance_hash": gate["acceptance_hash"],
        "successor_cells": [
            {"cell_id": "CELL-01-A.01-1", "independently_deliverable": True, "independently_d1_checkable": True, "dependencies": []},
            {"cell_id": "CELL-01-A.01-2", "independently_deliverable": True, "independently_d1_checkable": True, "dependencies": ["CELL-01-A.01-1"]},
        ],
    }
    assert_valid(tmp_path, trace)


def pin_observation(provenance: str, disposition: str, *, evidence: str | None) -> dict:
    return {
        "observation_id": f"PIN-{provenance}",
        "thread_id": "THREAD-CHECKER-A",
        "pinned": True,
        "provenance": provenance,
        "owner_evidence_ref": evidence,
        "disposition": disposition,
        "patrol_unpinned": False,
        "agent_action_event_ids": [],
    }


def test_creation_dispatch_and_method_states_do_not_trigger_pin(tmp_path: Path) -> None:
    trace = valid_trace()
    assert not trace["pin_observations"]
    assert all(item["action"] not in {"SET_THREAD_PINNED_TRUE", "SET_THREAD_PINNED_FALSE"} for item in trace["events"])
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize(
    "role_kind",
    ["SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"],
)
def test_all_method_roles_permanently_deny_pin_capability(tmp_path: Path, role_kind: str) -> None:
    trace = valid_trace()
    row = next(item for item in trace["method_role_capabilities"] if item["role_kind"] == role_kind)
    row["set_thread_pinned"] = True
    assert_invalid(tmp_path, trace, "set_thread_pinned capability")


def test_pin_capability_matrix_contains_only_canonical_clk_roles(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["method_role_capabilities"] = [
        item
        for item in trace["method_role_capabilities"]
        if item["role_kind"] in {"SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"}
    ]
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize("extra_role", ["ROUTER", "GRAPHER", "PATROL"])
def test_extra_role_in_canonical_clk_pin_matrix_is_rejected(tmp_path: Path, extra_role: str) -> None:
    trace = valid_trace()
    trace["method_role_capabilities"] = [
        item
        for item in trace["method_role_capabilities"]
        if item["role_kind"] in {"SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"}
    ]
    trace["method_role_capabilities"].append(
        {"role_id": f"EXTRA-{extra_role}", "role_kind": extra_role, "set_thread_pinned": False}
    )
    assert_invalid(tmp_path, trace, "is too long")


def test_patrol_cannot_pin(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(
        event("EVENT-PATROL-PIN", 4, "PATROL", "PATROL-RUN-001", "SET_THREAD_PINNED_TRUE")
    )
    assert_invalid(tmp_path, trace, "patrol must not Pin")


def test_patrol_pin_capability_is_independently_denied(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["patrols"][0]["set_thread_pinned"] = True
    assert_invalid(tmp_path, trace, "False was expected")


@pytest.mark.parametrize("provenance", ["OWNER_UI", "OWNER_EXPLICIT_AUTHORIZATION"])
def test_owner_pin_provenance_is_allowed(tmp_path: Path, provenance: str) -> None:
    trace = valid_trace()
    trace["pin_observations"].append(pin_observation(provenance, "ALLOWED", evidence="OWNER-EVIDENCE-001"))
    assert_valid(tmp_path, trace)


def test_agent_pin_emits_stable_unauthorized_violation(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].append(
        event("EVENT-AGENT-PIN", 4, "WORKER", "WORKER-A", "SET_THREAD_PINNED_TRUE")
    )
    observation = pin_observation("AGENT_TOOL_CALL", "UNAUTHORIZED_THREAD_PIN", evidence=None)
    observation["agent_action_event_ids"] = ["EVENT-AGENT-PIN"]
    trace["pin_observations"].append(observation)
    assert_invalid(tmp_path, trace, "UNAUTHORIZED_THREAD_PIN")


def test_unknown_pin_provenance_requires_bound_patrol_alert_without_unpin(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["pin_observations"].append(
        pin_observation("UNKNOWN", "PIN_PROVENANCE_UNKNOWN", evidence=None)
    )
    assert_invalid(tmp_path, trace, "PIN_PROVENANCE_UNKNOWN requires a bound PATROL_ALERT")

    trace["events"].extend(
        [
            event(
                "EVENT-PIN-UNKNOWN-ALERT",
                4,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_ALERT",
                data=patrol_alert_data(
                    "FINDING-PIN-UNKNOWN",
                    "PIN_PROVENANCE_UNKNOWN",
                    "PIN-UNKNOWN",
                ),
            ),
            event(
                "EVENT-PIN-UNKNOWN-STATUS",
                4,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_STATUS",
                data=patrol_status_data(
                    "ALERTS_EMITTED",
                    finding_ids=["FINDING-PIN-UNKNOWN"],
                ),
            ),
        ]
    )
    assert_valid(tmp_path, trace)
    trace["pin_observations"][0]["patrol_unpinned"] = True
    assert_invalid(tmp_path, trace, "must not unpin unknown provenance")


@pytest.mark.parametrize(
    ("project_workload", "interval"),
    [("LOW", 10), ("MEDIUM", 15), ("HIGH", 30)],
)
def test_project_workload_maps_to_patrol_interval(
    tmp_path: Path, project_workload: str, interval: int
) -> None:
    trace = valid_trace()
    trace["patrols"][0].update(project_workload=project_workload, interval_minutes=interval)
    assert_valid(tmp_path, trace)


def test_pin_then_unpin_keeps_original_agent_violation(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].extend(
        [
            event("EVENT-AGENT-PIN", 4, "WORKER", "WORKER-A", "SET_THREAD_PINNED_TRUE"),
            event("EVENT-AGENT-UNPIN", 4, "WORKER", "WORKER-A", "SET_THREAD_PINNED_FALSE"),
        ]
    )
    observation = pin_observation("AGENT_TOOL_CALL", "UNAUTHORIZED_THREAD_PIN", evidence=None)
    observation["agent_action_event_ids"] = ["EVENT-AGENT-PIN", "EVENT-AGENT-UNPIN"]
    trace["pin_observations"].append(observation)
    assert_invalid(tmp_path, trace, "UNAUTHORIZED_THREAD_PIN")


def test_archive_lifecycle_is_independent_from_pin(tmp_path: Path) -> None:
    trace = valid_trace()
    trace["events"].extend(
        [
            event("EVENT-ARCHIVE", 4, "SUPERVISOR", "SUPERVISOR-001", "THREAD_ARCHIVE"),
            event("EVENT-UNARCHIVE", 4, "SUPERVISOR", "SUPERVISOR-001", "THREAD_UNARCHIVE"),
        ]
    )
    assert_valid(tmp_path, trace)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("supervisor_wait", "Supervisor wait_threads"),
        ("missing_capability", "capability preflight"),
        ("delivery_as_accepted", "accepted CELL count"),
        ("spawn_agent", "subagent capability evidence"),
        ("dispatch_without_pass", "dispatch requires current PASS"),
        ("worker_split", "Worker must not split"),
        ("unknown_capacity", "unknown capability"),
        ("agent_pin", "UNAUTHORIZED_THREAD_PIN"),
        ("unknown_pin_unpin", "must not unpin unknown provenance"),
        ("missing_wake", "CELL dispatch requires one wake lifecycle"),
        ("missing_checker_progress", "D1 verdict requires exactly one Checker progress update"),
        ("missing_supervisor_progress", "material progress trigger requires exactly one Supervisor progress update"),
        ("unknown_pin_without_alert", "PIN_PROVENANCE_UNKNOWN requires a bound PATROL_ALERT"),
        ("arbitrary_patrol_status", "patrol status must bind the complete mechanical check set"),
        ("checker_wrong_trigger", "D1 verdict requires exactly one Checker progress update"),
        ("supervisor_wrong_trigger", "material progress trigger requires exactly one Supervisor progress update"),
    ],
)
def test_critical_invalid_traces_fail_closed_in_normal_and_optimized_modes(
    tmp_path: Path, mutation: str, message: str
) -> None:
    trace = valid_trace()
    if mutation == "supervisor_wait":
        trace["events"].append(event("EVENT-BAD", 4, "SUPERVISOR", "SUPERVISOR-001", "WAIT_THREADS"))
    elif mutation == "missing_capability":
        trace["worker_bindings"][0]["capabilities"]["read_thread"] = False
    elif mutation == "delivery_as_accepted":
        next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-DELIVERED")["data"]["accepted_cell_count"] = 1
    elif mutation == "spawn_agent":
        trace["events"].append(event("EVENT-BAD", 4, "SYSTEM", "CODEX", "OBSERVE_SPAWN_AGENT"))
    elif mutation == "dispatch_without_pass":
        trace["device_capacity_profile"]["unknown_capabilities"] = ["AVAILABLE_RAM"]
        trace["cell_capacity_gates"][0]["result"] = "CAPACITY_BLOCKED"
    elif mutation == "worker_split":
        trace["events"].append(
            event("EVENT-BAD", 4, "WORKER", "WORKER-A", "CELL_SPLIT", scope=wake_scope())
        )
    elif mutation == "unknown_capacity":
        trace["device_capacity_profile"]["unknown_capabilities"] = ["AVAILABLE_RAM"]
    elif mutation == "agent_pin":
        trace["events"].append(
            event("EVENT-BAD-PIN", 4, "WORKER", "WORKER-A", "SET_THREAD_PINNED_TRUE")
        )
        observation = pin_observation("AGENT_TOOL_CALL", "UNAUTHORIZED_THREAD_PIN", evidence=None)
        observation["agent_action_event_ids"] = ["EVENT-BAD-PIN"]
        trace["pin_observations"].append(observation)
    elif mutation == "unknown_pin_unpin":
        observation = pin_observation("UNKNOWN", "PIN_PROVENANCE_UNKNOWN", evidence=None)
        observation["patrol_unpinned"] = True
        trace["pin_observations"].append(observation)
    elif mutation == "missing_wake":
        trace["events"] = [item for item in trace["events"] if item["action"] not in {
            "WAKE_ATTEMPT", "WAKE_ACK", "MECHANICAL_CHECKER_STARTED", "CHECKER_START",
            "TEMP_HEARTBEAT_UPSERT", "TEMP_HEARTBEAT_DELETE", "PENDING_WAKE_WRITE",
            "PENDING_WAKE_CONSUME",
        }]
    elif mutation == "missing_checker_progress":
        trace["events"] = [item for item in trace["events"] if item["event_id"] != "EVENT-PROGRESS-D1"]
    elif mutation == "missing_supervisor_progress":
        trace["events"] = [item for item in trace["events"] if item["action"] != "SUPERVISOR_PROGRESS"]
    elif mutation == "unknown_pin_without_alert":
        trace["pin_observations"].append(
            pin_observation("UNKNOWN", "PIN_PROVENANCE_UNKNOWN", evidence=None)
        )
    elif mutation == "arbitrary_patrol_status":
        trace["events"].append(
            event(
                "EVENT-BAD-PATROL",
                4,
                "PATROL",
                "PATROL-RUN-001",
                "PATROL_STATUS",
                data={"reason": "EVERYTHING_FINE_WITHOUT_CHECKS"},
            )
        )
    elif mutation == "checker_wrong_trigger":
        progress = next(item for item in trace["events"] if item["event_id"] == "EVENT-PROGRESS-D1")
        progress["data"].update(trigger_event_id="EVENT-ACK", trigger_receipt_id=None)
    elif mutation == "supervisor_wrong_trigger":
        progress = next(item for item in trace["events"] if item["event_id"] == "EVENT-SUPERVISOR-CANDIDATE")
        progress["data"]["trigger_event_id"] = "EVENT-D2-A"
    path = write_trace(tmp_path, trace, f"{mutation}.yaml")
    for optimized in (False, True):
        result = run_trace(path, optimized=optimized)
        if result.returncode != 2:
            pytest.fail(f"optimized={optimized}: {result.stdout=} {result.stderr=}")
        if message not in result.stderr:
            pytest.fail(f"optimized={optimized}: expected {message!r} in {result.stderr!r}")
