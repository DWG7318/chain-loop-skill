from __future__ import annotations

import json
import importlib.util
from copy import deepcopy
from pathlib import Path

import yaml
import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "chain-loop-skill"
TEMPLATES = SKILL / "templates"
SCHEMAS = SKILL / "schemas"
RECEIPT_CHAIN_VALIDATOR = ROOT / "scripts" / "validate_receipt_chain.py"


def load_yaml(name: str) -> dict:
    return yaml.safe_load((TEMPLATES / name).read_text(encoding="utf-8"))


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate(schema_name: str, document: dict) -> None:
    validator = Draft202012Validator(load_schema(schema_name))
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    assert not errors, "\n".join(error.message for error in errors)


def load_receipt_chain_validator():
    spec = importlib.util.spec_from_file_location("clk_receipt_chain", RECEIPT_CHAIN_VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_templates_validate_against_schemas() -> None:
    validate("chain-level-plan.schema.json", load_yaml("chain-level-plan.yaml"))
    validate("runtime-state-index.schema.json", load_yaml("runtime-state-index.yaml"))


def test_receipts_use_one_strong_envelope() -> None:
    names = [
        "d0-worker-receipt.yaml",
        "d1-checker-receipt.yaml",
        "d2-go-verification-receipt.yaml",
        "level-verification-receipt.yaml",
        "d3-run-verification-receipt.yaml",
    ]
    required = {
        "receipt_id",
        "receipt_type",
        "run_id",
        "feature_slice_id",
        "baseline_id",
        "baseline_version",
        "baseline_hash",
        "contract_id",
        "contract_version",
        "contract_hash",
        "attempt_id",
        "candidate_digest",
        "actor_id",
        "responsibility",
        "verification_context_ref",
        "environment_fingerprint",
        "workspace_id",
        "evidence_path",
        "evidence_hash",
        "issued_at",
        "consumed_receipts",
        "invalidates",
        "supersedes",
        "result",
        "failure_reason",
    }
    for name in names:
        receipt = load_yaml(name)
        assert required <= set(receipt), name
        validate("receipt-envelope.schema.json", receipt)


def test_verification_layers_use_distinct_attempt_context_workspace_and_evidence() -> None:
    receipts = [
        load_yaml("d2-go-verification-receipt.yaml"),
        load_yaml("level-verification-receipt.yaml"),
        load_yaml("d3-run-verification-receipt.yaml"),
    ]
    for field in ("attempt_id", "verification_context_ref", "workspace_id", "evidence_path"):
        values = [receipt[field] for receipt in receipts]
        assert len(values) == len(set(values)), field


def test_level_barrier_receipt_reconstructs_the_decision() -> None:
    receipt = load_yaml("level-barrier-receipt.yaml")
    required = {
        "baseline_id",
        "baseline_version",
        "baseline_hash",
        "level_id",
        "barrier_claim",
        "required_assignments",
        "optional_assignments",
        "level_verification_required",
        "level_verification_decision_ref",
        "level_verification_receipt_ref",
        "candidate_set_hash",
        "atomic_transition_id",
        "supervisor_id",
        "issued_at",
        "result",
    }
    assert required <= set(receipt)
    assert receipt["required_assignments"][0]["resolution"] == "D2_PASS"
    assert receipt["required_assignments"][0]["d2_receipt_hash"]


def test_all_amendment_types_exist_and_validate() -> None:
    expected = {
        "chain-amendment.yaml": "CHAIN_AMENDMENT",
        "level-amendment.yaml": "LEVEL_AMENDMENT",
        "go-amendment.yaml": "GO_AMENDMENT",
    }
    for name, amendment_type in expected.items():
        amendment = load_yaml(name)
        assert amendment["amendment_type"] == amendment_type
        validate("amendment-envelope.schema.json", amendment)


def test_owner_acceptance_is_run_scoped_and_uses_complete_verdict_enum() -> None:
    acceptance = load_yaml("owner-acceptance.yaml")
    assert acceptance["acceptance_scope"] == "RUN_PRODUCT_ONLY"
    assert acceptance["project_security_closed"] is False
    assert acceptance["delivery_authorized"] is False
    assert set(acceptance["allowed_verdicts"]) == {
        "LOOP_OWNER_ACCEPTED",
        "LOOP_PRODUCT_REWORK",
        "PRODUCT_DEFINITION_CHANGE",
        "NEW_FEATURE_REQUEST",
    }
    run_receipt = load_yaml("clk-run-receipt.yaml")
    assert set(run_receipt["allowed_owner_verdicts"]) == set(acceptance["allowed_verdicts"])


def test_receipt_chain_binds_consumed_hashes_and_candidate() -> None:
    module = load_receipt_chain_validator()
    receipts = [
        load_yaml("d0-worker-receipt.yaml"),
        load_yaml("d1-checker-receipt.yaml"),
        load_yaml("d2-go-verification-receipt.yaml"),
    ]
    module.validate_receipt_chain(receipts)


def test_receipt_chain_rejects_candidate_mismatch() -> None:
    module = load_receipt_chain_validator()
    d0 = load_yaml("d0-worker-receipt.yaml")
    d1 = deepcopy(load_yaml("d1-checker-receipt.yaml"))
    d1["consumed_receipts"][0]["receipt_hash"] = module.receipt_document_hash(d0)
    d1["candidate_digest"] = "0" * 64
    with pytest.raises(module.ReceiptChainValidationError, match="candidate mismatch"):
        module.validate_receipt_chain([d0, d1])


def test_receipt_chain_rejects_consumed_hash_mismatch() -> None:
    module = load_receipt_chain_validator()
    d0 = load_yaml("d0-worker-receipt.yaml")
    d1 = deepcopy(load_yaml("d1-checker-receipt.yaml"))
    d1["consumed_receipts"][0]["receipt_hash"] = "0" * 64
    with pytest.raises(module.ReceiptChainValidationError, match="consumed Receipt hash mismatch"):
        module.validate_receipt_chain([d0, d1])
