#!/usr/bin/env python3
"""Validate CLK topology-fault records and their minimal Receipt closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "chain-loop-skill" / "schemas" / "topology-fault-record.schema.json"
STATE_HYPOTHESIS_STATUS = {
    "OPEN": "ACTIVE",
    "FALSIFIED": "FALSIFIED",
    "SUPERSEDED": "FALSIFIED",
    "ROUTED": "CONFIRMED",
    "RESOLVED": "CONFIRMED",
}
NATIVE_ROUTES = {
    "CHAIN_LOCAL": {"CELL_REWORK", "GO_REWORK_REQUIRED"},
    "CROSS_CHAIN_COMPOSITION": {"LEVEL_REVERIFICATION"},
    "LEVEL_BARRIER": {"BARRIER_RECALCULATION"},
}
ESCALATION_ROUTES = {
    "PLAN_DEFECT",
    "CALABASH_REVIEW_REQUIRED",
    "METHOD_BOUNDARY_EXCEEDED",
}


class TopologyFaultValidationError(ValueError):
    """Raised when topology-fault evidence violates CLK invariants."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TopologyFaultValidationError(message)


def validate_schema(record: Any) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "<root>"
        raise TopologyFaultValidationError(f"topology fault schema at {location}: {error.message}")


def downstream_closure(changed: set[str], edges: list[dict[str, Any]]) -> set[str]:
    closure = set(changed)
    while True:
        before = len(closure)
        for edge in edges:
            if set(edge["consumed_receipt_ids"]) & closure:
                closure.add(edge["consumer_receipt_id"])
        if len(closure) == before:
            return closure


def cell_scope_matches_go(scope_id: str, go_id: str) -> bool:
    return go_id.startswith("GO-") and scope_id.startswith(f"CELL-{go_id[3:]}.")


def source_scope_matches(record: dict[str, Any], scope_id: str) -> bool:
    layer = record["source_layer"]
    go_ids = {candidate["go_id"] for candidate in record["candidate_refs"]}
    if layer in {"D0", "D1"}:
        return any(cell_scope_matches_go(scope_id, go_id) for go_id in go_ids)
    if layer == "D2":
        return scope_id in go_ids
    if layer in {"LEVEL", "BARRIER"}:
        return scope_id == record["level_id"]
    return layer == "D3" and scope_id == record["run_id"]


def canonical_go_id(level_id: str, chain_id: str) -> str | None:
    if not level_id.startswith("LEVEL-") or not chain_id.startswith("CHAIN-"):
        return None
    return f"GO-{level_id[6:]}-{chain_id[6:]}"


def validate_record(record: dict[str, Any]) -> None:
    validate_schema(record)
    affected = set(record["affected_chain_ids"])
    candidate_chains = {item["chain_id"] for item in record["candidate_refs"]}
    candidate_go_ids = {item["go_id"] for item in record["candidate_refs"]}
    require(candidate_chains == affected, "candidate_refs must cover exactly the affected Chains")
    expected_status = STATE_HYPOTHESIS_STATUS[record["record_state"]]
    require(
        record["hypothesis"]["status"] == expected_status,
        f"record_state {record['record_state']} requires hypothesis.status {expected_status}",
    )
    source_attempts = [
        attempt for attempt in record["attempt_refs"]
        if attempt["layer"] == record["source_layer"]
    ]
    require(
        bool(source_attempts),
        "attempt_refs must bind the source_layer",
    )
    require(
        all(source_scope_matches(record, attempt["scope_id"]) for attempt in source_attempts),
        "source attempt scope must match the affected CELL/GO, Level, or Run",
    )
    content_hashed_evidence = {item["evidence_path"] for item in record["evidence_refs"]}
    require(
        set(record["hypothesis"]["evidence_refs"]) <= content_hashed_evidence,
        "hypothesis evidence must be content-hash bound by top-level evidence_refs",
    )

    closure = record["closure"]
    catalog_items = closure["receipt_catalog"]
    require(bool(catalog_items), "receipt_catalog must be non-empty for every fault_class")
    catalog_ids = [item["receipt_id"] for item in catalog_items]
    require(len(catalog_ids) == len(set(catalog_ids)), "receipt_catalog IDs must be unique")
    catalog = {item["receipt_id"]: item for item in catalog_items}
    for edge in closure["consumption_edges"]:
        require(edge["consumer_receipt_id"] in catalog, "consumption edge consumer must exist in receipt_catalog")
        require(
            set(edge["consumed_receipt_ids"]) <= set(catalog),
            "consumption edge inputs must exist in receipt_catalog",
        )
    changed = set(closure["changed_receipt_ids"])
    invalidated = set(closure["invalidated_receipt_ids"])
    preserved = set(closure["preserved_receipt_ids"])
    require(changed <= set(catalog), "changed receipts must exist in receipt_catalog")
    expected_invalidated = downstream_closure(changed, closure["consumption_edges"])
    require(
        invalidated == expected_invalidated,
        "invalidation closure must equal receipt-consumption closure",
    )
    require(invalidated <= set(catalog), "invalidated receipts must exist in receipt_catalog")
    require(preserved <= set(catalog), "preserved receipts must exist in receipt_catalog")
    require(not invalidated & preserved, "a Receipt cannot be both invalidated and preserved")
    require(
        preserved == set(catalog) - invalidated,
        "preserved receipts must equal catalog minus invalidated receipts",
    )

    if record["fault_class"] == "CHAIN_LOCAL":
        require(bool(changed), "CHAIN_LOCAL requires at least one changed Receipt")
        require(bool(invalidated), "CHAIN_LOCAL requires a non-empty invalidation closure")
        require(
            all(
                catalog[receipt_id]["scope_id"] in candidate_go_ids
                or any(
                    cell_scope_matches_go(catalog[receipt_id]["scope_id"], go_id)
                    for go_id in candidate_go_ids
                )
                for receipt_id in changed
            ),
            "CHAIN_LOCAL changed Receipts must belong to an affected candidate scope",
        )
    elif record["fault_class"] == "CROSS_CHAIN_COMPOSITION":
        d2_scopes = {
            item["scope_id"] for item in catalog_items if item["layer"] == "D2"
        }
        require(
            candidate_go_ids <= d2_scopes,
            "CROSS_CHAIN_COMPOSITION requires a D2 Receipt for every affected GO",
        )
    elif record["fault_class"] == "LEVEL_BARRIER":
        require(
            closure["barrier_recalculation_only"] is True
            and not changed
            and not invalidated
            and preserved == set(catalog),
            "LEVEL_BARRIER must preserve all technical Receipts and recalculate only BARRIER",
        )

    actual_reverification = {
        (item["layer"], item["scope_id"]) for item in closure["reverification"]
    }
    if invalidated:
        expected_reverification = {
            (catalog[receipt_id]["layer"], catalog[receipt_id]["scope_id"])
            for receipt_id in invalidated
        }
        require(
            actual_reverification == expected_reverification,
            "reverification must equal the invalidated Receipt scope closure",
        )
    elif record["fault_class"] == "CROSS_CHAIN_COMPOSITION":
        require(
            actual_reverification == {("LEVEL", record["level_id"])},
            "unchanged cross-Chain candidates require only fresh LEVEL reverification",
        )
    elif record["fault_class"] == "LEVEL_BARRIER":
        require(
            closure["barrier_recalculation_only"] is True
            and actual_reverification == {("BARRIER", record["level_id"])},
            "Barrier-only correction must re-evaluate only BARRIER",
        )

    if closure["barrier_recalculation_only"]:
        require(record["fault_class"] == "LEVEL_BARRIER", "only LEVEL_BARRIER may be Barrier-only")
        require(not changed and not invalidated, "Barrier-only correction cannot invalidate product Receipts")
        require(preserved == set(catalog), "Barrier-only correction must preserve every catalogued Receipt")

    controls = record["healthy_chain_controls"]
    require(
        len({control["chain_id"] for control in controls}) == len(controls),
        "healthy control Chain IDs must be unique",
    )
    require(
        len({control["d2_receipt_id"] for control in controls}) == len(controls),
        "healthy control D2 Receipt IDs must be unique",
    )
    for control in controls:
        require(control["level_id"] == record["level_id"], "healthy control must be in the same Level")
        require(control["chain_id"] not in affected, "affected Chain cannot be its own healthy control")
        receipt_id = control["d2_receipt_id"]
        require(
            receipt_id in catalog and receipt_id in preserved,
            "healthy control D2 must be preserved, never substituted or invalidated",
        )
        catalog_receipt = catalog[receipt_id]
        require(catalog_receipt["layer"] == "D2", "healthy control Receipt must have layer D2")
        require(
            control["d2_receipt_hash"] == catalog_receipt["receipt_hash"],
            "healthy control D2 hash must match receipt_catalog",
        )
        expected_scope = canonical_go_id(control["level_id"], control["chain_id"])
        require(
            expected_scope is not None and catalog_receipt["scope_id"] == expected_scope,
            "healthy control D2 scope must match its same-Level Chain GO",
        )

    trigger = record["escalation_trigger"]
    route = record["route"]
    if route in ESCALATION_ROUTES or trigger is not None:
        require(trigger == route, "escalation trigger and route must match")
    else:
        require(
            route in NATIVE_ROUTES[record["fault_class"]],
            "route is invalid for fault_class",
        )


def validate_records(records: list[dict[str, Any]]) -> None:
    require(bool(records), "at least one topology fault record is required")
    for record in records:
        validate_record(record)
    ids = [record["fault_record_id"] for record in records]
    require(len(ids) == len(set(ids)), "fault_record_id values must be unique")
    by_id = {record["fault_record_id"]: record for record in records}
    active_by_series: dict[str, int] = {}
    for record in records:
        if record["hypothesis"]["status"] == "ACTIVE":
            series = record["fault_series_id"]
            active_by_series[series] = active_by_series.get(series, 0) + 1
        previous_id = record["supersedes"]
        next_id = record["superseded_by"]
        require(previous_id != record["fault_record_id"], "record cannot supersede itself")
        require(next_id != record["fault_record_id"], "record cannot be superseded by itself")
        if previous_id is not None:
            require(previous_id in by_id, "supersedes must reference a supplied record")
            previous = by_id[previous_id]
            require(previous["fault_series_id"] == record["fault_series_id"], "supersession must stay in one fault series")
            require(previous["record_state"] in {"FALSIFIED", "SUPERSEDED"}, "superseded hypothesis must be sealed")
            require(previous["superseded_by"] == record["fault_record_id"], "supersession links must be reciprocal")
        if record["record_state"] in {"FALSIFIED", "SUPERSEDED"}:
            require(next_id in by_id, "sealed record superseded_by must reference a supplied successor")
        else:
            require(next_id is None, "only a sealed record may declare superseded_by")
        if next_id is not None:
            successor = by_id[next_id]
            require(successor["fault_series_id"] == record["fault_series_id"], "supersession must stay in one fault series")
            require(successor["supersedes"] == record["fault_record_id"], "supersession links must be reciprocal")
    require(
        all(count <= 1 for count in active_by_series.values()),
        "at most one active hypothesis is allowed per fault series",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args(argv)
    try:
        records = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in args.records]
        validate_records(records)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, TopologyFaultValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: CLK topology fault record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
