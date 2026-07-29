#!/usr/bin/env python3
"""Validate a frozen CLK Chain/Level baseline without using assertions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


class PlanValidationError(ValueError):
    """Raised when a Chain/Level plan violates a CLK hard invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanValidationError(message)


def non_empty_text(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be non-empty text")
    return value.strip()


def validate_plan(data: Any) -> None:
    require(isinstance(data, dict), "plan root must be a mapping")
    non_empty_text(data.get("run_id"), "run_id")
    non_empty_text(data.get("baseline_id"), "baseline_id")
    require(isinstance(data.get("baseline_version"), int) and data["baseline_version"] > 0,
            "baseline_version must be a positive integer")
    baseline_hash = non_empty_text(data.get("baseline_hash"), "baseline_hash")
    require(len(baseline_hash) == 64, "baseline_hash must be a 64-character SHA-256 digest")
    require(data.get("state") == "FROZEN", "plan state must be FROZEN")

    chains = data.get("chains")
    require(isinstance(chains, list) and len(chains) >= 2,
            "CLK requires at least two non-empty Chains")
    chain_map: dict[str, list[str]] = {}
    all_go_list: list[str] = []
    for index, chain in enumerate(chains):
        require(isinstance(chain, dict), f"chains[{index}] must be a mapping")
        chain_id = non_empty_text(chain.get("chain_id"), f"chains[{index}].chain_id")
        require(chain_id not in chain_map, "Chain IDs must be unique")
        non_empty_text(chain.get("intent"), f"{chain_id}.intent")
        go_order = chain.get("go_order")
        require(isinstance(go_order, list) and bool(go_order),
                "CLK requires at least two non-empty Chains")
        require(all(isinstance(go_id, str) and go_id for go_id in go_order),
                f"{chain_id}.go_order must contain non-empty GO IDs")
        require(len(go_order) == len(set(go_order)), f"{chain_id}.go_order contains duplicate GO IDs")
        chain_map[chain_id] = list(go_order)
        all_go_list.extend(go_order)
    require(len(all_go_list) == len(set(all_go_list)), "GO IDs must be globally unique")

    levels = data.get("levels")
    require(isinstance(levels, list) and bool(levels), "levels must be a non-empty list")
    level_ids: list[str] = []
    ordinals: list[int] = []
    assigned: set[str] = set()
    actual_by_chain: dict[str, list[str]] = {chain_id: [] for chain_id in chain_map}
    for index, level in enumerate(levels):
        require(isinstance(level, dict), f"levels[{index}] must be a mapping")
        level_id = non_empty_text(level.get("level_id"), f"levels[{index}].level_id")
        ordinal = level.get("ordinal")
        require(isinstance(ordinal, int) and ordinal > 0, "Level ordinal must be a positive integer")
        level_ids.append(level_id)
        ordinals.append(ordinal)
        assignments = level.get("assignments")
        require(isinstance(assignments, list) and bool(assignments),
                f"{level_id}.assignments must be a non-empty list")
        chains_in_level: set[str] = set()
        for assignment_index, assignment in enumerate(assignments):
            require(isinstance(assignment, dict),
                    f"{level_id}.assignments[{assignment_index}] must be a mapping")
            chain_id = non_empty_text(assignment.get("chain_id"), "assignment.chain_id")
            go_id = non_empty_text(assignment.get("go_id"), "assignment.go_id")
            require(chain_id in chain_map, f"unknown Chain {chain_id}")
            require(chain_id not in chains_in_level, "one GO per Chain per Level")
            require(go_id in chain_map[chain_id], f"{go_id} does not belong to {chain_id}")
            require(go_id not in assigned, f"GO {go_id} is assigned more than once")
            require(isinstance(assignment.get("required"), bool),
                    f"{go_id}.required must be boolean")
            chains_in_level.add(chain_id)
            assigned.add(go_id)
            actual_by_chain[chain_id].append(go_id)
        non_empty_text(level.get("barrier_claim"), f"{level_id}.barrier_claim")
        require(isinstance(level.get("level_verification_required"), bool),
                f"{level_id}.level_verification_required must be boolean")
        non_empty_text(level.get("verification_reason"), f"{level_id}.verification_reason")

    require(len(level_ids) == len(set(level_ids)), "Level IDs must be unique")
    require(len(ordinals) == len(set(ordinals)), "Level ordinals must be unique")
    require(ordinals == sorted(ordinals), "Level ordinals must be strictly increasing")
    for chain_id, expected in chain_map.items():
        require(actual_by_chain[chain_id] == expected,
                f"{chain_id} assignment does not follow frozen go_order")
    require(assigned == set(all_go_list),
            f"every GO must be assigned exactly once; mismatch={sorted(assigned ^ set(all_go_list))}")


def load_plan(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args(argv)
    try:
        validate_plan(load_plan(args.plan))
    except (OSError, yaml.YAMLError, PlanValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: Chain/Level plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
