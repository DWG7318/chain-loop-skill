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
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *(str(FIXTURES / name) for name in names)],
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


def test_falsified_hypothesis_is_sealed_and_superseded_by_a_new_record() -> None:
    module = load_validator()
    first = load_fixture("valid-chain-local.yaml")
    first["record_state"] = "FALSIFIED"
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
    with pytest.raises(module.TopologyFaultValidationError, match="Barrier-only correction cannot"):
        module.validate_records([fault])


def test_fault_record_strongly_binds_receipt_and_evidence_content() -> None:
    fault = load_fixture("valid-chain-local.yaml")
    for receipt in fault["closure"]["receipt_catalog"]:
        assert len(receipt["receipt_hash"]) == 64
    for evidence in fault["evidence_refs"]:
        assert evidence["evidence_path"]
        assert len(evidence["evidence_hash"]) == 64
