#!/usr/bin/env python3
"""Validate the mutable CLK runtime index against its frozen evidence history."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "chain-loop-skill" / "schemas" / "runtime-state-index.schema.json"
OPEN_LEVEL_STATES = {"LEVEL_ACTIVE", "LEVEL_WAITING_VERIFICATION", "LEVEL_WAITING_BARRIER"}
OPTIONAL_TERMINAL_STATES = {"D2_PASS", "CANCELLED", "DEFERRED_BY_AMENDMENT", "SUPERSEDED"}


class RuntimeValidationError(ValueError):
    """Raised when runtime state violates a CLK invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeValidationError(message)


def unique(values: list[Any], message: str) -> None:
    require(len(values) == len(set(values)), message)


def validate_schema(data: Any) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda error: list(error.path))
    if errors:
        raise RuntimeValidationError(f"runtime schema: {errors[0].message}")


def validate_runtime(data: Any) -> None:
    validate_schema(data)
    levels = data["levels"]
    level_ids = [level.get("level_id") for level in levels]
    unique(level_ids, "Level IDs must be unique")
    unique([level.get("ordinal") for level in levels], "Level ordinals must be unique")
    open_levels = [level for level in levels if level.get("state") in OPEN_LEVEL_STATES]
    if data["state"] in {"RUNNING", "BLOCKED"}:
        require(len(open_levels) == 1, "runtime must have exactly one open Level")
        require(data["open_level_id"] == open_levels[0]["level_id"],
                "open_level_id must identify exactly one open Level")
    else:
        require(len(open_levels) <= 1, "runtime must have at most one open Level")

    chains = data["chains"]
    chain_ids = [chain.get("chain_id") for chain in chains]
    unique(chain_ids, "Chain IDs must be unique")
    chain_map = {chain["chain_id"]: chain for chain in chains}
    for chain in chains:
        active_go_ids = chain.get("active_go_ids")
        require(isinstance(active_go_ids, list), "active_go_ids must be a list")
        require(len(active_go_ids) <= 1, "runtime permits at most one ACTIVE GO per Chain")

    gos = data["gos"]
    go_ids = [go.get("go_id") for go in gos]
    unique(go_ids, "GO IDs must be unique")
    go_map = {go["go_id"]: go for go in gos}
    for chain_id, chain in chain_map.items():
        for go_id in chain.get("active_go_ids", []):
            require(go_id in go_map, f"active GO {go_id} is missing from runtime")
            go = go_map[go_id]
            require(go.get("chain_id") == chain_id, f"active GO {go_id} belongs to another Chain")
            require(go.get("state") == "ACTIVE", f"active_go_ids entry {go_id} is not ACTIVE")
            require(go.get("level_id") == data["open_level_id"],
                    "an ACTIVE GO must belong to the open Level")
    for go in gos:
        if go.get("state") == "ACTIVE":
            require(go.get("chain_id") in chain_map, f"GO {go.get('go_id')} has an unknown Chain")
            require(go.get("go_id") in chain_map[go["chain_id"]].get("active_go_ids", []),
                    f"ACTIVE GO {go.get('go_id')} is absent from its Chain index")

    attempts = data["verification_attempts"]
    unique([attempt.get("attempt_id") for attempt in attempts],
           "verification attempt IDs must be unique")
    unique([attempt.get("context_ref") for attempt in attempts],
           "verification context refs must be unique")
    unique([attempt.get("workspace_id") for attempt in attempts],
           "verification workspace IDs must be unique")
    unique([attempt.get("evidence_path") for attempt in attempts],
           "verification evidence paths must be unique")
    for attempt in attempts:
        for field in ("layer", "scope_id", "attempt_id", "context_ref", "workspace_id", "evidence_path"):
            require(isinstance(attempt.get(field), str) and bool(attempt[field]),
                    f"verification attempt {field} must be non-empty")

    barrier = data.get("barrier_evaluation")
    if barrier and barrier.get("result") == "LEVEL_BARRIER_PASSED":
        require(barrier.get("level_id") == data["open_level_id"],
                "Barrier must close the currently open Level")
        required_assignments = barrier.get("required_assignments", [])
        optional_assignments = barrier.get("optional_assignments", [])
        expected_required = {
            go["go_id"] for go in gos
            if go.get("level_id") == barrier["level_id"] and go.get("required") is True
        }
        expected_optional = {
            go["go_id"] for go in gos
            if go.get("level_id") == barrier["level_id"] and go.get("required") is False
        }
        actual_required = [assignment.get("go_id") for assignment in required_assignments]
        actual_optional = [assignment.get("go_id") for assignment in optional_assignments]
        require(
            len(actual_required) == len(set(actual_required))
            and len(actual_optional) == len(set(actual_optional))
            and set(actual_required) == expected_required
            and set(actual_optional) == expected_optional,
            "Barrier assignment coverage mismatch",
        )
        for assignment in required_assignments:
            require(assignment.get("resolution") == "D2_PASS",
                    "Required GO requires D2_PASS while it remains in the Baseline")
            require(bool(assignment.get("d2_receipt_id")) and bool(assignment.get("d2_receipt_hash")),
                    "Required GO D2_PASS must bind a D2 Receipt ID and Hash")
        for assignment in optional_assignments:
            require(assignment.get("state") in OPTIONAL_TERMINAL_STATES,
                    "Optional GO must reach a non-active terminal state before Barrier PASS")
        if barrier.get("level_verification_required"):
            require(bool(barrier.get("level_verification_receipt_ref")),
                    "required Level Verification must bind its Receipt")
        candidate_set_hash = barrier.get("candidate_set_hash")
        require(isinstance(candidate_set_hash, str) and len(candidate_set_hash) == 64,
                "Barrier must bind a 64-character candidate_set_hash")
        require(bool(barrier.get("atomic_transition_id")),
                "Barrier PASS requires an atomic transition ID")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    args = parser.parse_args(argv)
    try:
        data = yaml.safe_load(args.state.read_text(encoding="utf-8"))
        validate_runtime(data)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, RuntimeValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: CLK runtime state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
