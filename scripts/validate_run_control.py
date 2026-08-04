#!/usr/bin/env python3
"""Validate CLK 2.5.0 Worker wake, patrol, capacity, and layered progress traces."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "chain-loop-skill" / "schemas" / "run-control-trace.schema.json"
WAKE_OFFSETS = {1: 0, 2: 2, 3: 4}
PATROL_INTERVAL = {"LOW": 30, "MEDIUM": 15, "HIGH": 10}
FORBIDDEN_AGENT_EVIDENCE = {
    "OBSERVE_SPAWN_AGENT",
    "OBSERVE_DELEGATE_TASK",
    "OBSERVE_HIDDEN_AGENT",
    "OBSERVE_BACKGROUND_AGENT",
    "SPAWN_AGENT",
    "DELEGATE_TASK",
}
PATROL_ACTIONS = {
    "PENDING_WAKE_CONSUME",
    "PATROL_STATUS",
    "PATROL_ALERT",
    "PATROL_HEARTBEAT_DELETE",
    "PATROL_CLOSED",
    "PATROL_ARCHIVE",
}
MATERIAL_PROGRESS_TRIGGERS = {
    "GO_MILESTONE",
    "D2_VERDICT",
    "LEVEL_VERIFIED",
    "REQUIRED_SET_AMENDMENT",
    "D3_VERDICT",
    "OWNER_ACCEPTANCE",
}
WALL_TIME_COMPONENTS = {
    "implementation_seconds",
    "build_seconds",
    "focused_test_seconds",
    "checker_seconds",
    "evidence_hash_cleanup_seconds",
    "rollback_retry_seconds",
    "external_tool_seconds",
}
WORKER_MESSAGE = re.compile(r"^(GO-[A-Za-z0-9-]+) CELL ([1-9][0-9]*)/([1-9][0-9]*) .+$")


class RunControlValidationError(ValueError):
    """Raised when a run-control trace violates a CLK invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RunControlValidationError(message)


def unique(values: list[Any], message: str) -> None:
    require(len(values) == len(set(values)), message)


def validate_schema(trace: Any) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(trace), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(item) for item in error.path) or "<root>"
        raise RunControlValidationError(f"run control schema at {location}: {error.message}")


def required_sets(trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = trace["required_sets"]
    unique([item["version"] for item in items], "Required-set versions must be unique")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        go_ids = item["required_go_ids"]
        cell_rows = item["required_cells"]
        unique([row["go_id"] for row in cell_rows], "Required CELL GO rows must be unique")
        require({row["go_id"] for row in cell_rows} == set(go_ids), "Required CELL rows must cover Required GOs")
        all_cells = [cell for row in cell_rows for cell in row["cell_ids"]]
        unique(all_cells, "Required CELL IDs must be unique within a Required set")
        result[item["version"]] = item
    require(trace["run"]["required_set_version"] in result, "Run must reference an existing Required set")
    return result


def required_cell_map(item: dict[str, Any]) -> dict[str, set[str]]:
    return {row["go_id"]: set(row["cell_ids"]) for row in item["required_cells"]}


def validate_bindings(trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bindings = trace["worker_bindings"]
    unique([item["worker_id"] for item in bindings], "Worker bindings must be unique")
    unique([item["checker_id"] for item in bindings], "Checker bindings must be unique")
    unique([item["checker_thread_id"] for item in bindings], "Checker thread bindings must be unique")
    for item in bindings:
        require(item["role"] == "WORKER", "wake binding role must be WORKER")
        require(all(item["capabilities"].values()), "Worker dispatch capability preflight must PASS")
    return {item["worker_id"]: item for item in bindings}


def validate_patrol(trace: dict[str, Any]) -> dict[str, Any]:
    require(len(trace["patrols"]) == 1, "exactly one patrol is required per Run")
    patrol = trace["patrols"][0]
    run_id = trace["run"]["run_id"]
    require(patrol["heartbeat_id"] == f"PATROL::{run_id}", "patrol heartbeat must be deterministic for the Run")
    require(patrol["heartbeat_count"] == 1, "exactly one patrol heartbeat is required")
    require(
        patrol["interval_minutes"] == PATROL_INTERVAL[patrol["difficulty"]],
        "patrol interval must match frozen Run difficulty",
    )
    if trace["run"]["state"] == "LOOP_TERMINAL":
        require(patrol["heartbeat_state"] == "DELETED", "terminal patrol heartbeat must be deleted")
    else:
        require(patrol["heartbeat_state"] == "ACTIVE", "non-terminal patrol heartbeat must remain active")
    return patrol


def validate_event_order(trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
    events = trace["events"]
    unique([item["event_id"] for item in events], "event IDs must be unique")
    require(
        [item["minute"] for item in events] == sorted(item["minute"] for item in events),
        "events must be ordered by injected minute",
    )
    for item in events:
        require(item["run_id"] == trace["run"]["run_id"], "event Run identity mismatch")
    return {item["event_id"]: item for item in events}


def validate_actor_boundaries(trace: dict[str, Any], patrol: dict[str, Any]) -> None:
    for item in trace["events"]:
        action = item["action"]
        actor = item["actor_kind"]
        if action in FORBIDDEN_AGENT_EVIDENCE:
            raise RunControlValidationError("subagent capability evidence is forbidden in CLK")
        if actor == "SUPERVISOR" and action == "WAIT_THREADS":
            raise RunControlValidationError("Supervisor wait_threads is forbidden")
        if action in {"READ_THREAD_SNAPSHOT", "LIST_THREADS_SNAPSHOT"}:
            require(item["data"].get("timeout_ms") == 0, "thread snapshot must use timeoutMs:0")
        if actor == "PATROL":
            require(item["actor_id"] == patrol["patrol_id"], "patrol event must use the unique Run patrol")
            require(action in PATROL_ACTIONS, "patrol action exceeds mechanical status/evidence/alert authority")
        if actor == "VERIFICATION":
            require(action in {"D2_VERDICT", "D3_VERDICT"}, "Verification may emit formal verdicts only")
        if action == "TERM_CLASSIFICATION":
            require(item["data"].get("classification") == "SUBTASK", "subtask terminology classification is invalid")
        if action == "OBSERVE_VISIBLE_TASK":
            require(
                item["data"].get("visible") is True and item["data"].get("stable_thread_id") is True,
                "visible peer task requires a stable visible thread identity",
            )
        if action == "CELL_SPLIT" and actor == "WORKER":
            raise RunControlValidationError("Worker must not split a CELL")


def validate_pin_policy(trace: dict[str, Any], event_index: dict[str, dict[str, Any]]) -> None:
    rows = trace["method_role_capabilities"]
    required_kinds = {"SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION", "ROUTER", "GRAPHER", "PATROL"}
    unique([item["role_id"] for item in rows], "method-role Pin capability IDs must be unique")
    unique([item["role_kind"] for item in rows], "method-role Pin capability kinds must be unique")
    require({item["role_kind"] for item in rows} == required_kinds, "Pin capability matrix must cover every method-role kind")
    require(not any(item["set_thread_pinned"] for item in rows), "every method-role set_thread_pinned capability must be denied")

    observations = trace["pin_observations"]
    unique([item["observation_id"] for item in observations], "Pin observation IDs must be unique")
    pin_events = [item for item in trace["events"] if item["action"] == "SET_THREAD_PINNED_TRUE"]
    unpin_events = [item for item in trace["events"] if item["action"] == "SET_THREAD_PINNED_FALSE"]
    for item in pin_events:
        if item["actor_kind"] == "PATROL":
            raise RunControlValidationError("patrol must not Pin a task")
    for item in unpin_events:
        if item["actor_kind"] == "PATROL":
            raise RunControlValidationError("patrol must not Pin or unpin a task")

    observed_agent_events: set[str] = set()
    unknown_exists = False
    for observation in observations:
        provenance = observation["provenance"]
        disposition = observation["disposition"]
        action_ids = observation["agent_action_event_ids"]
        if provenance in {"OWNER_UI", "OWNER_EXPLICIT_AUTHORIZATION"}:
            require(disposition == "ALLOWED", "Owner Pin provenance must be allowed")
            require(bool(observation["owner_evidence_ref"]), "Owner Pin requires explicit provenance evidence")
            require(not action_ids, "Owner Pin must not cite Agent Pin actions")
            require(observation["patrol_unpinned"] is False, "patrol must not unpin Owner provenance")
        elif provenance == "UNKNOWN":
            unknown_exists = True
            require(disposition == "PIN_PROVENANCE_UNKNOWN", "unknown Pin provenance requires PIN_PROVENANCE_UNKNOWN")
            require(observation["owner_evidence_ref"] is None and not action_ids, "unknown Pin provenance must not guess evidence")
            require(observation["patrol_unpinned"] is False, "patrol must not unpin unknown provenance")
        elif provenance == "AGENT_TOOL_CALL":
            require(disposition == "UNAUTHORIZED_THREAD_PIN", "Agent Pin requires UNAUTHORIZED_THREAD_PIN")
            require(action_ids, "Agent Pin observation must cite its tool-call evidence")
            for event_id in action_ids:
                require(event_id in event_index, "Agent Pin observation cites unknown event")
                observed_agent_events.add(event_id)
            require(
                any(event_index[event_id]["action"] == "SET_THREAD_PINNED_TRUE" for event_id in action_ids),
                "Agent Pin observation must retain the original Pin call",
            )
            raise RunControlValidationError("UNAUTHORIZED_THREAD_PIN")
    if unknown_exists:
        require(not unpin_events, "unknown Pin provenance must not be auto-unpinned")
    unattributed = [item for item in pin_events if item["event_id"] not in observed_agent_events]
    if unattributed:
        raise RunControlValidationError("UNAUTHORIZED_THREAD_PIN")


def expected_progress_identity(run_id: str, scope: dict[str, Any]) -> str:
    return "|".join(
        [run_id, scope["required_set_version"], scope["go_id"], scope["cell_id"], scope["round_id"]]
    )


def validate_worker_message(item: dict[str, Any]) -> None:
    scope = item["scope"]
    data = item["data"]
    message = data.get("message", "")
    match = WORKER_MESSAGE.fullmatch(message)
    require(match is not None, "scoped Worker message must contain GO_ID and CELL n/N")
    require(
        match.group(1) == scope["go_id"]
        and int(match.group(2)) == scope["cell_ordinal"]
        and int(match.group(3)) == scope["required_cell_total"],
        "scoped Worker message position must match frozen scope",
    )
    signal = data.get("signal")
    if signal == "DELIVERY":
        require("已交付" in message and "检查" in message, "scoped Worker message requires delivered/check semantics")
    elif signal == "BLOCKED":
        require("BLOCKED" in message, "BLOCKED Worker message must name the condition")
    elif signal == "EXECUTION_FAILURE":
        require("EXECUTION_FAILURE" in message, "execution failure message must name the condition")
    else:
        raise RunControlValidationError("Worker wake signal must be DELIVERY, BLOCKED, or EXECUTION_FAILURE")


def validate_worker_wakes(trace: dict[str, Any], bindings: dict[str, dict[str, Any]], patrol: dict[str, Any]) -> None:
    events = trace["events"]
    attempts_by_wake: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in events:
        if item["action"] == "WAKE_ATTEMPT":
            require(item["actor_kind"] == "WORKER", "only WORKER may use the wake ladder")
            require(item["actor_id"] in bindings, "wake Worker must have a frozen Checker binding")
            require(item["wake_id"] is not None and item["scope"] is not None, "wake attempt requires wake and scope identity")
            attempts_by_wake[item["wake_id"]].append(item)
        elif item["action"] in {"WAKE_ACK", "MECHANICAL_CHECKER_STARTED", "PENDING_WAKE_WRITE"}:
            require(item["wake_id"] is not None, f"{item['action']} requires wake identity")

    for wake_id, attempts in attempts_by_wake.items():
        attempts.sort(key=lambda item: item["data"]["level"])
        first = attempts[0]
        binding = bindings[first["actor_id"]]
        scope = first["scope"]
        levels = [item["data"]["level"] for item in attempts]
        early_successes = [
            item for item in events
            if item["wake_id"] == wake_id and item["action"] in {"WAKE_ACK", "MECHANICAL_CHECKER_STARTED"}
        ]
        if early_successes:
            first_success_minute = min(item["minute"] for item in early_successes)
            require(not any(item["minute"] > first_success_minute for item in attempts), "wake attempt occurred after wake success")
        require(levels == list(range(1, len(levels) + 1)) and len(levels) <= 3, "wake levels must be contiguous 1..3")
        require(first["minute"] == 0, "wake Level 1 must start at T+0")
        identity = expected_progress_identity(trace["run"]["run_id"], scope)
        messages = set()
        identities = set()
        for item in attempts:
            level = item["data"]["level"]
            require(item["minute"] == WAKE_OFFSETS[level], f"wake Level {level} must use injected T+{WAKE_OFFSETS[level]}")
            require(item["scope"] == scope, "all wake levels must keep the same frozen scope")
            validate_worker_message(item)
            messages.add(item["data"]["message"])
            identities.add(item["data"].get("progress_identity"))
            require(item["data"].get("guessed_id") is False, "Level 2 must not guess Checker identity")
            require(item["data"].get("created_replacement_checker") is False, "wake ladder must not create a replacement Checker")
            require(item["data"].get("target_thread_id") == binding["checker_thread_id"], "wake must target the original Checker thread")
            if level == 1:
                require(item["data"].get("target_host_id") == binding["checker_host_id"], "Level 1 must target the frozen Checker host")
            if level == 2:
                data = item["data"]
                require(data.get("inspected_original_thread") is True, "Level 2 must inspect the original Checker")
                require(data.get("resolved_checker_id") == binding["checker_id"], "Level 2 must resolve the same Checker")
                require(data.get("resolved_from_frozen_registry") is True, "Level 2 must use the frozen role registry")
                if data.get("target_host_id") != binding["checker_host_id"]:
                    require(data.get("observed_host_mismatch") is True, "Level 2 host change requires observed host mismatch")
                if data.get("observed_archived"):
                    require(data.get("unarchived_original") is True, "Level 2 must unarchive the original Checker")
            if level == 3:
                heartbeat_id = f"WAKE::{trace['run']['run_id']}::{binding['checker_id']}::{scope['go_id']}::{scope['cell_id']}::{scope['round_id']}"
                require(item["data"].get("temporary_heartbeat_id") == heartbeat_id, "Level 3 heartbeat must be deterministic")
                upserts = [
                    event for event in events
                    if event["action"] == "TEMP_HEARTBEAT_UPSERT" and event["wake_id"] == wake_id
                ]
                require(len(upserts) == 1, "Level 3 temporary heartbeat must be unique")
                require(
                    upserts[0]["actor_kind"] == "WORKER"
                    and upserts[0]["minute"] == 4
                    and upserts[0]["data"].get("heartbeat_id") == heartbeat_id
                    and upserts[0]["data"].get("unique_count") == 1,
                    "Level 3 temporary heartbeat evidence is invalid",
                )
        require(messages and len(messages) == 1, "all wake levels must resend the same scoped Worker message")
        require(identities == {identity}, "all wake levels must keep the same progress identity")

        successes = [
            item for item in events
            if item["wake_id"] == wake_id and item["action"] in {"WAKE_ACK", "MECHANICAL_CHECKER_STARTED"}
        ]
        require(len(successes) <= 1, "wake may have at most one success signal")
        if successes:
            success = successes[0]
            require(success["actor_kind"] == "CHECKER" and success["actor_id"] == binding["checker_id"], "wake success must come from the original Checker")
            require(success["scope"] == scope, "WAKE_ACK must match Run/GO/CELL/Round scope")
            prior_attempts = [item for item in attempts if item["minute"] <= success["minute"]]
            last_attempt = max(prior_attempts, key=lambda item: item["minute"])
            require(success["minute"] <= last_attempt["minute"] + 2, "Worker wait exceeds two minutes for a wake level")
            require(not any(item["minute"] > success["minute"] for item in attempts), "wake attempt occurred after wake success")
            checker_actions = [item for item in events if item["wake_id"] == wake_id and item["actor_kind"] == "CHECKER"]
            require(checker_actions and checker_actions[0]["action"] in {"WAKE_ACK", "MECHANICAL_CHECKER_STARTED"}, "Checker first wake action must be WAKE_ACK")
            if levels[-1] == 3:
                deletes = [item for item in events if item["action"] == "TEMP_HEARTBEAT_DELETE" and item["wake_id"] == wake_id]
                require(len(deletes) == 1 and deletes[0]["actor_kind"] == "CHECKER", "Checker must delete the temporary heartbeat after ACK")
            require(not any(item["action"] == "PENDING_WAKE_WRITE" and item["wake_id"] == wake_id for item in events), "successful wake must not leave PENDING_WAKE")
        else:
            require(levels == [1, 2, 3], "unsuccessful wake must exhaust exactly three active attempts")
            pending = [item for item in events if item["action"] == "PENDING_WAKE_WRITE" and item["wake_id"] == wake_id]
            require(len(pending) == 1 and pending[0]["minute"] == 6, "three failures require one PENDING_WAKE at T+6")
            record = pending[0]
            require(record["actor_kind"] == "WORKER" and record["scope"] == scope, "PENDING_WAKE must retain Worker and scope identity")
            require(record["data"].get("attempt_levels") == [1, 2, 3] and len(record["data"].get("errors", [])) == 3, "PENDING_WAKE must bind all attempts and errors")
            require(record["data"].get("progress_identity") == identity and record["data"].get("message") in messages, "PENDING_WAKE must keep the same progress identity")
            consumes = [item for item in events if item["action"] == "PENDING_WAKE_CONSUME" and item["wake_id"] == wake_id]
            require(len(consumes) == 1 and consumes[0]["actor_id"] == patrol["patrol_id"], "PENDING_WAKE must be consumed by the unique patrol")

    for item in events:
        if item["action"] in {"WAKE_ACK", "MECHANICAL_CHECKER_STARTED", "PENDING_WAKE_WRITE"}:
            require(item["wake_id"] in attempts_by_wake, f"{item['action']} references an unknown wake")


def estimated_cell_cost(gate: dict[str, Any], load: dict[str, Any]) -> dict[str, int]:
    cost = gate["cost"]
    return {
        "wall_seconds": sum(cost[name] for name in WALL_TIME_COMPONENTS)
        + load["full_regression_seconds"]
        + load["context_reload_seconds"],
        "peak_ram_mb": max(cost["implementation_peak_ram_mb"], load["peak_ram_mb"]),
        "disk_mb": cost["generated_artifact_mb"] + load["evidence_mb"],
        "context_tokens": cost["context_tokens"] + load["context_tokens"],
        "evidence_mb": cost["evidence_mb"] + load["evidence_mb"],
        "concurrency_units": cost["concurrency_units"],
        "max_single_command_seconds": cost["max_single_command_seconds"],
    }


def expected_capacity_result(gate: dict[str, Any], profile: dict[str, Any], load: dict[str, Any]) -> str:
    if profile["unknown_capabilities"]:
        return "CAPACITY_BLOCKED"
    demand = estimated_cell_cost(gate, load)
    exceeded = (
        demand["wall_seconds"] > profile["max_cell_wall_seconds"]
        or demand["peak_ram_mb"] > profile["available_ram_mb"]
        or demand["disk_mb"] > profile["disk_free_mb"]
        or demand["context_tokens"] > profile["context_budget_tokens"]
        or demand["evidence_mb"] > profile["evidence_budget_mb"]
        or demand["concurrency_units"] > profile["safe_command_concurrency"]
        or demand["max_single_command_seconds"] > profile["max_single_command_seconds"]
        or load["external_service_calls"] > profile["external_service_limit"]
    )
    if not exceeded:
        return "PASS"
    return "SPLIT_REQUIRED" if gate["splittable"] else "CAPACITY_BLOCKED"


def validate_capacity(trace: dict[str, Any], event_index: dict[str, dict[str, Any]]) -> None:
    profile = trace["device_capacity_profile"]
    loads = trace["engineering_load_snapshots"]
    gates = trace["cell_capacity_gates"]
    unique([item["version"] for item in loads], "cumulative load versions must be unique")
    unique([item["gate_id"] for item in gates], "CELL capacity gate IDs must be unique")
    load_map = {item["version"]: item for item in loads}
    gate_map = {item["gate_id"]: item for item in gates}
    feedback = sorted(
        [item for item in trace["events"] if item["action"] == "LOAD_FEEDBACK"],
        key=lambda item: item["minute"],
    )
    for item in feedback:
        version = item["data"].get("new_load_snapshot_version")
        require(item["actor_kind"] == "SUPERVISOR" and version in load_map, "LOAD_FEEDBACK must bind a known Supervisor load snapshot")
    for gate in gates:
        require(gate["capacity_profile_version"] == profile["version"], "capacity gate profile version is stale")
        require(gate["load_snapshot_version"] in load_map, "capacity gate load snapshot is unknown")
        applicable = [item for item in feedback if item["minute"] < gate["evaluated_minute"]]
        if applicable:
            latest = applicable[-1]["data"]["new_load_snapshot_version"]
            require(gate["load_snapshot_version"] == latest, "future gate must use latest cumulative load")
        expected = expected_capacity_result(gate, profile, load_map[gate["load_snapshot_version"]])
        if profile["unknown_capabilities"]:
            require(gate["result"] == "CAPACITY_BLOCKED", "unknown capability must fail closed as CAPACITY_BLOCKED")
        require(gate["result"] == expected, f"capacity gate result must be {expected}")
        split = gate["split"]
        if gate["result"] == "SPLIT_REQUIRED":
            require(split is not None, "SPLIT_REQUIRED gate must define pre-dispatch successors")
            require(
                split["go_outcome_hash"] == gate["go_outcome_hash"]
                and split["acceptance_hash"] == gate["acceptance_hash"],
                "pre-dispatch split must preserve GO outcome and acceptance",
            )
            unique([item["cell_id"] for item in split["successor_cells"]], "split successor CELL IDs must be unique")
        else:
            require(split is None, "non-split capacity result must not define successor CELLs")

    for item in trace["events"]:
        action = item["action"]
        data = item["data"]
        if action == "CELL_DISPATCH":
            gate_id = data.get("gate_id")
            require(item["actor_kind"] == "CHECKER", "CELL dispatch must remain Checker-authorized")
            require(gate_id in gate_map, "CELL dispatch requires a known capacity gate")
            gate = gate_map[gate_id]
            require(gate["result"] == "PASS", "CELL dispatch requires current PASS capacity gate")
            require(gate["evaluated_minute"] <= item["minute"], "CELL dispatch cannot precede capacity evaluation")
            require(item["scope"] and item["scope"]["go_id"] == gate["go_id"] and item["scope"]["cell_id"] == gate["cell_id"], "CELL dispatch scope must match capacity gate")
            require(data.get("plan_version") == gate["plan_version"], "CELL dispatch plan version must match capacity gate")
        elif action == "CELL_SCOPE_EXCEEDED":
            require(item["actor_kind"] == "WORKER", "CELL_SCOPE_EXCEEDED belongs to Worker")
            require(
                bool(data.get("checkpoint_id"))
                and isinstance(data.get("evidence_hash"), str)
                and len(data["evidence_hash"]) == 64
                and data.get("worker_continued") is False,
                "CELL_SCOPE_EXCEEDED requires immutable checkpoint/evidence and stop",
            )
        elif action == "POST_DISPATCH_CELL_SPLIT":
            successors = data.get("successor_cell_ids", [])
            require(data.get("planning_defect") == "POST_DISPATCH_CELL_SPLIT", "post-dispatch split must record its planning defect")
            if len(successors) >= 3:
                require(
                    data.get("severity") == "CELL_OVERSIZE_SEVERE"
                    and data.get("reassess_remaining_plan") is True
                    and data.get("reassess_device_profile") is True
                    and data.get("reassess_load_model") is True,
                    "three or more successors require CELL_OVERSIZE_SEVERE and full reassessment",
                )
        elif action == "PRE_DISPATCH_CELL_SPLIT":
            gate_id = data.get("gate_id")
            require(item["actor_kind"] == "CHECKER" and gate_id in gate_map, "pre-dispatch split requires Checker and known gate")
            gate = gate_map[gate_id]
            require(gate["result"] == "SPLIT_REQUIRED", "pre-dispatch split requires SPLIT_REQUIRED gate")
            require(data.get("go_outcome_hash") == gate["go_outcome_hash"] and data.get("acceptance_hash") == gate["acceptance_hash"], "pre-dispatch split must preserve GO outcome and acceptance")


def validate_progress(trace: dict[str, Any], sets: dict[str, dict[str, Any]], event_index: dict[str, dict[str, Any]]) -> None:
    current_version = trace["run"]["required_set_version"]
    accepted_receipts: dict[str, tuple[str, str, str]] = {}
    accepted_cells: dict[str, str] = {}
    d2_verdicts: dict[str, tuple[str, str]] = {}
    d2_gos: set[str] = set()
    candidate_ready: set[str] = set()
    completed_levels: set[str] = set()

    for item in trace["events"]:
        action = item["action"]
        data = item["data"]
        current_set = sets[current_version]
        cell_map = required_cell_map(current_set)
        required_gos = set(current_set["required_go_ids"])
        if action == "D1_VERDICT":
            require(item["actor_kind"] == "CHECKER" and item["scope"] is not None, "D1 verdict must be Checker-scoped")
            scope = item["scope"]
            require(data.get("required_set_version") == current_version, "D1 verdict Required-set version is stale")
            require(scope["go_id"] in cell_map and scope["cell_id"] in cell_map[scope["go_id"]], "D1 verdict CELL is not currently Required")
            receipt_id = data.get("receipt_id")
            payload = (scope["go_id"], scope["cell_id"], data.get("result"))
            if receipt_id in accepted_receipts:
                require(accepted_receipts[receipt_id] == payload, "duplicate D1 Receipt identity drift")
            elif data.get("result") == "PASS" and data.get("effective") is True:
                accepted_receipts[receipt_id] = payload
                accepted_cells.setdefault(scope["cell_id"], receipt_id)
        elif action == "CHECKER_PROGRESS":
            require(item["actor_kind"] == "CHECKER" and item["scope"] is not None, "Checker progress must remain Checker-scoped")
            scope = item["scope"]
            version = scope.get("required_set_version")
            require(version == current_version, "Checker progress must show current Required-set version")
            go_id = scope["go_id"]
            require(go_id in cell_map, "Checker progress GO is not currently Required")
            total = len(cell_map[go_id])
            accepted = len(cell_map[go_id] & set(accepted_cells))
            require(data.get("required_cell_total") == total, "Checker progress Required CELL denominator mismatch")
            require(data.get("accepted_cell_count") == accepted, "Checker accepted CELL count must derive from effective D1 PASS Receipts")
            require(data.get("state") in {"DELIVERED", "D1_ACCEPTED"}, "Checker progress state must preserve DELIVERED/D1_ACCEPTED layering")
        elif action == "GO_MILESTONE":
            require(item["actor_kind"] == "CHECKER" and item["scope"] is not None, "GO milestone belongs to Checker")
            go_id = item["scope"]["go_id"]
            require(go_id in cell_map and cell_map[go_id] <= set(accepted_cells), "GO milestone requires all Required CELLs D1 accepted")
            require(data.get("accepted_cell_count") == data.get("required_cell_total") == len(cell_map[go_id]), "GO milestone must show CELL N/N accepted")
            require(data.get("required_go_total") == len(required_gos), "GO milestone Required GO denominator mismatch")
            status = data.get("status")
            require(status in {"GO_CANDIDATE_READY", "VERIFYING", "D2_VERIFIED"}, "GO milestone status is invalid")
            if status == "D2_VERIFIED":
                require(go_id in d2_gos, "GO_CANDIDATE_READY does not equal D2_VERIFIED")
            candidate_ready.add(go_id)
        elif action == "D2_VERDICT":
            require(item["actor_kind"] == "VERIFICATION" and item["scope"] is not None, "D2 verdict belongs to Verification")
            go_id = item["scope"]["go_id"]
            require(data.get("required_set_version") == current_version, "D2 verdict Required-set version is stale")
            require(go_id in candidate_ready, "D2 verdict requires GO_CANDIDATE_READY")
            require(data.get("result") == "GO_VERIFIED", "only GO_VERIFIED enters the D2 numerator")
            verdict_id = data.get("verdict_id")
            if verdict_id in d2_verdicts:
                require(d2_verdicts[verdict_id] == (go_id, current_version), "duplicate D2 verdict identity drift")
            else:
                d2_verdicts[verdict_id] = (go_id, current_version)
                d2_gos.add(go_id)
        elif action == "LEVEL_VERIFIED":
            completed_levels.add(data.get("level_id"))
        elif action == "REQUIRED_SET_AMENDMENT":
            require(item["actor_kind"] == "SUPERVISOR", "Required-set amendment belongs to Supervisor")
            new_version = data.get("new_required_set_version")
            require(new_version in sets, "Required-set amendment must activate an existing version")
            preserved_d1 = set(data.get("preserved_d1_receipt_ids", []))
            preserved_d2 = set(data.get("preserved_d2_verdict_ids", []))
            require(preserved_d1 <= set(accepted_receipts), "amendment preserves unknown D1 Receipt")
            require(preserved_d2 <= set(d2_verdicts), "amendment preserves unknown D2 verdict")
            current_version = new_version
            new_cells = required_cell_map(sets[current_version])
            allowed_cells = {cell for cells in new_cells.values() for cell in cells}
            accepted_receipts = {key: value for key, value in accepted_receipts.items() if key in preserved_d1 and value[1] in allowed_cells}
            accepted_cells = {value[1]: key for key, value in accepted_receipts.items()}
            new_gos = set(sets[current_version]["required_go_ids"])
            d2_verdicts = {key: value for key, value in d2_verdicts.items() if key in preserved_d2 and value[0] in new_gos}
            d2_gos = {value[0] for value in d2_verdicts.values()}
            candidate_ready = {go_id for go_id, cells in new_cells.items() if cells <= set(accepted_cells)}
        elif action == "SUPERVISOR_PROGRESS":
            require(item["actor_kind"] == "SUPERVISOR", "global progress belongs to Supervisor")
            trigger_id = data.get("trigger_event_id")
            require(trigger_id in event_index and event_index[trigger_id]["action"] in MATERIAL_PROGRESS_TRIGGERS, "Supervisor progress trigger must be a substantive GO/Level/Graph/Run change")
            require(event_index[trigger_id]["minute"] <= item["minute"], "Supervisor progress cannot precede its trigger")
            require(data.get("required_set_version") == current_version, "Supervisor progress must show current Required-set version")
            verified = len(d2_gos & required_gos)
            require(data.get("current_level_verified_go_count") == verified, "Supervisor D2 verified GO count mismatch")
            require(data.get("current_level_required_go_total") == len(required_gos), "Supervisor Required GO denominator mismatch")
            require(data.get("completed_level_count") == len(completed_levels), "Supervisor completed Level count mismatch")
            require(data.get("total_level_count") == trace["run"]["total_level_count"], "Supervisor total Level denominator mismatch")
            if data.get("state") == "D2_VERIFIED":
                require(verified > 0, "D2 verified GO count cannot be claimed without a current verdict")
            require(data.get("state") in {"GO_CANDIDATE_READY", "D2_VERIFIED", "RUN_VERIFIED", "OWNER_ACCEPTED"}, "Supervisor progress state is not layer-specific")


def validate_terminal(trace: dict[str, Any], patrol: dict[str, Any]) -> None:
    events = trace["events"]
    if trace["run"]["state"] == "PAUSED":
        require(bool(trace["run"]["pause_reason"]), "formal pause requires a reason")
        for item in events:
            if item["action"] == "PATROL_ALERT":
                require(item["data"].get("reason") != "STALL", "formal pause must not be reported as unexplained stall")
    if trace["run"]["state"] != "LOOP_TERMINAL":
        return
    require(trace["run"]["terminal_confirmed"] is True, "LOOP_TERMINAL must be formally confirmed")
    actions = [item["action"] for item in events]
    sequence = ["LOOP_TERMINAL_CONFIRMED", "PATROL_HEARTBEAT_DELETE", "PATROL_CLOSED", "PATROL_ARCHIVE"]
    require(len(actions) >= 4 and actions[-4:] == sequence, "terminal patrol sequence must delete heartbeat, close, and archive")


def validate_trace(trace: dict[str, Any]) -> None:
    validate_schema(trace)
    sets = required_sets(trace)
    bindings = validate_bindings(trace)
    patrol = validate_patrol(trace)
    event_index = validate_event_order(trace)
    validate_pin_policy(trace, event_index)
    validate_actor_boundaries(trace, patrol)
    validate_worker_wakes(trace, bindings, patrol)
    validate_capacity(trace, event_index)
    validate_progress(trace, sets, event_index)
    validate_terminal(trace, patrol)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args(argv)
    try:
        trace = yaml.safe_load(args.trace.read_text(encoding="utf-8"))
        validate_trace(trace)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, RunControlValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: CLK run control trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
