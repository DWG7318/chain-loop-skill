from __future__ import annotations

import importlib.util
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_topology_fault.py"
FIXTURES = ROOT / "tests" / "fixtures" / "topology-faults"


def run_validator(*names: str) -> subprocess.CompletedProcess[str]:
    return run_record_paths([FIXTURES / name for name in names])


def run_record_paths(
    paths: list[Path], *, optimized: bool = False
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable]
    if optimized:
        command.append("-O")
    command.extend([str(VALIDATOR), *(str(path) for path in paths)])
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_validator():
    spec = importlib.util.spec_from_file_location("clk_topology_fault", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fixture(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def invalid_cross_field_record(case: str) -> dict:
    fault = deepcopy(load_fixture("valid-chain-local.yaml"))
    if case == "unpartitioned_catalog":
        fault["closure"]["receipt_catalog"].append(
            {
                "receipt_id": "RECEIPT-D2-UNACCOUNTED",
                "receipt_hash": "9" * 64,
                "layer": "D2",
                "scope_id": "GO-01-Z",
            }
        )
    elif case == "empty_chain_local_closure":
        fault["healthy_chain_controls"] = []
        fault["closure"].update(
            receipt_catalog=[],
            consumption_edges=[],
            changed_receipt_ids=[],
            invalidated_receipt_ids=[],
            preserved_receipt_ids=[],
            reverification=[{"layer": "D2", "scope_id": "GO-01-A"}],
        )
    elif case == "healthy_control_hash_mismatch":
        fault["healthy_chain_controls"][0]["d2_receipt_hash"] = "8" * 64
    elif case == "unbound_hypothesis_evidence":
        fault["hypothesis"]["evidence_refs"] = ["coordination/evidence/unbound.md"]
    elif case == "source_attempt_scope_mismatch":
        fault["attempt_refs"][0]["scope_id"] = "GO-99-Z"
    elif case == "superseded_active_without_links":
        fault["record_state"] = "SUPERSEDED"
    elif case == "chain_local_wrong_route":
        fault["route"] = "BARRIER_RECALCULATION"
    elif case == "level_barrier_product_invalidation":
        fault = deepcopy(load_fixture("valid-level-barrier.yaml"))
        fault["closure"]["barrier_recalculation_only"] = False
        fault["closure"]["changed_receipt_ids"] = ["RECEIPT-D2-01-A"]
        fault["closure"]["invalidated_receipt_ids"] = ["RECEIPT-D2-01-A"]
        fault["closure"]["preserved_receipt_ids"] = ["RECEIPT-D2-01-B"]
        fault["closure"]["reverification"] = [{"layer": "D2", "scope_id": "GO-01-A"}]
    else:  # pragma: no cover - guarded by the parametrization below
        raise AssertionError(case)
    return fault


@pytest.mark.parametrize(
    "fixture",
    ["valid-chain-local.yaml", "valid-cross-chain.yaml", "valid-level-barrier.yaml"],
)
def test_valid_topology_fault_classes_pass(fixture: str) -> None:
    result = run_validator(fixture)
    assert result.returncode == 0, result.stderr
    assert "PASS: CLK topology fault record" in result.stdout


@pytest.mark.parametrize(
    ("fixture", "message"),
    [
        ("invalid-nonminimal-closure.yaml", "invalidation closure must equal receipt-consumption closure"),
        ("invalid-unproven-control.yaml", "comparability_proven"),
    ],
)
def test_invalid_topology_fault_records_are_rejected(fixture: str, message: str) -> None:
    result = run_validator(fixture)
    assert result.returncode == 2
    assert message in result.stderr


def test_only_one_active_hypothesis_exists_per_fault_series() -> None:
    module = load_validator()
    first = load_fixture("valid-chain-local.yaml")
    second = deepcopy(first)
    second["fault_record_id"] = "TOPOLOGY-FAULT-CHAIN-A-002"
    second["hypothesis"]["hypothesis_id"] = "HYPOTHESIS-CHAIN-A-002"
    with pytest.raises(module.TopologyFaultValidationError, match="at most one active hypothesis"):
        module.validate_records([first, second])


@pytest.mark.parametrize("sealed_state", ["FALSIFIED", "SUPERSEDED"])
def test_falsified_hypothesis_is_sealed_and_superseded_by_a_new_record(
    sealed_state: str,
) -> None:
    module = load_validator()
    first = load_fixture("valid-chain-local.yaml")
    first["record_state"] = sealed_state
    first["hypothesis"]["status"] = "FALSIFIED"
    first["superseded_by"] = "TOPOLOGY-FAULT-CHAIN-A-002"
    second = deepcopy(load_fixture("valid-chain-local.yaml"))
    second["fault_record_id"] = "TOPOLOGY-FAULT-CHAIN-A-002"
    second["hypothesis"]["hypothesis_id"] = "HYPOTHESIS-CHAIN-A-002"
    second["supersedes"] = first["fault_record_id"]
    module.validate_records([first, second])


def test_barrier_only_fault_has_no_product_receipt_invalidation() -> None:
    fault = load_fixture("valid-level-barrier.yaml")
    assert fault["closure"]["changed_receipt_ids"] == []
    assert fault["closure"]["invalidated_receipt_ids"] == []
    assert fault["closure"]["reverification"] == [
        {"layer": "BARRIER", "scope_id": "LEVEL-01"}
    ]


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("acceptance_substitute", "acceptance_substitute"),
        ("creates_same_level_dependency", "creates_same_level_dependency"),
    ],
)
def test_healthy_chain_control_cannot_accept_or_feed_the_failed_chain(
    field: str, message: str
) -> None:
    module = load_validator()
    fault = load_fixture("valid-chain-local.yaml")
    fault["healthy_chain_controls"][0][field] = True
    with pytest.raises(module.TopologyFaultValidationError, match=message):
        module.validate_records([fault])


def test_fault_class_is_restricted_to_the_three_clk_topology_boundaries() -> None:
    module = load_validator()
    fault = load_fixture("valid-chain-local.yaml")
    fault["fault_class"] = "DYNAMIC_GRAPH"
    with pytest.raises(module.TopologyFaultValidationError, match="fault_class"):
        module.validate_records([fault])


def test_barrier_only_fault_rejects_product_receipt_invalidation() -> None:
    module = load_validator()
    fault = load_fixture("valid-level-barrier.yaml")
    fault["closure"]["changed_receipt_ids"] = ["RECEIPT-D2-01-A"]
    fault["closure"]["invalidated_receipt_ids"] = ["RECEIPT-D2-01-A"]
    fault["closure"]["preserved_receipt_ids"] = ["RECEIPT-D2-01-B"]
    fault["closure"]["reverification"] = [{"layer": "D2", "scope_id": "GO-01-A"}]
    with pytest.raises(module.TopologyFaultValidationError, match="LEVEL_BARRIER must preserve"):
        module.validate_records([fault])


def test_fault_record_strongly_binds_receipt_and_evidence_content() -> None:
    fault = load_fixture("valid-chain-local.yaml")
    for receipt in fault["closure"]["receipt_catalog"]:
        assert len(receipt["receipt_hash"]) == 64
    for evidence in fault["evidence_refs"]:
        assert evidence["evidence_path"]
        assert len(evidence["evidence_hash"]) == 64


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("unpartitioned_catalog", "preserved receipts must equal catalog minus invalidated receipts"),
        ("empty_chain_local_closure", "receipt_catalog"),
        ("healthy_control_hash_mismatch", "hash must match receipt_catalog"),
        ("unbound_hypothesis_evidence", "hypothesis evidence must be content-hash bound"),
        ("source_attempt_scope_mismatch", "source attempt scope"),
        ("superseded_active_without_links", "hypothesis.status"),
        ("chain_local_wrong_route", "route is invalid for fault_class"),
        ("level_barrier_product_invalidation", "LEVEL_BARRIER must preserve all technical Receipts"),
    ],
)
def test_cross_field_invalid_records_fail_with_and_without_assertions(
    tmp_path: Path, case: str, message: str
) -> None:
    path = tmp_path / f"{case}.yaml"
    path.write_text(
        yaml.safe_dump(invalid_cross_field_record(case), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    for optimized in (False, True):
        result = run_record_paths([path], optimized=optimized)
        assert result.returncode == 2, (optimized, result.stdout, result.stderr)
        assert message in result.stderr, (optimized, result.stderr)


@pytest.mark.parametrize(
    ("layer", "valid_scope", "invalid_scope"),
    [
        ("D0", "CELL-01-A.01", "CELL-99-Z.01"),
        ("D1", "CELL-01-A.01", "CELL-99-Z.01"),
        ("D2", "GO-01-A", "GO-99-Z"),
        ("LEVEL", "LEVEL-01", "LEVEL-99"),
        ("BARRIER", "LEVEL-01", "LEVEL-99"),
        ("D3", "RUN-001", "RUN-999"),
    ],
)
def test_source_attempt_scope_is_bound_to_the_fault_scope(
    layer: str, valid_scope: str, invalid_scope: str
) -> None:
    module = load_validator()
    fault = load_fixture("valid-chain-local.yaml")
    fault["source_layer"] = layer
    fault["attempt_refs"] = [
        {"layer": layer, "scope_id": valid_scope, "attempt_id": f"ATTEMPT-{layer}-001"}
    ]
    module.validate_records([fault])
    fault["attempt_refs"][0]["scope_id"] = invalid_scope
    with pytest.raises(module.TopologyFaultValidationError, match="source attempt scope"):
        module.validate_records([fault])
