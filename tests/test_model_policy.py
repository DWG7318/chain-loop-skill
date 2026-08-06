from __future__ import annotations

from copy import deepcopy
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_model_policy.py"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def evidence(name: str) -> dict[str, str]:
    return {"path": f"evidence/{name}.json", "sha256": digest(name)}


def receipt(kind: str, actor: str) -> dict[str, str]:
    return {
        "receipt_id": f"{kind.upper()}::{actor}",
        "status": "PASS",
        **evidence(f"{kind}-{actor}"),
    }


def scope(*, go_id: str | None = None, cell_id: str | None = None) -> dict[str, Any]:
    return {
        "run_id": "RUN-001",
        "go_id": go_id,
        "cell_id": cell_id,
        "round_id": "R01" if cell_id else None,
    }


def binding(
    actor_id: str,
    role_kind: str,
    actor_scope: dict[str, Any],
    *,
    model: str = "gpt-5.6-terra",
    tier: str = "TERRA_DEFAULT",
    reason: str = "DEFAULT_TECHNICAL",
    capability_class: str = "TECHNICAL_GENERAL",
) -> dict[str, Any]:
    suffix = actor_id.lower()
    return {
        "binding_id": f"BINDING::{actor_id}::001",
        "actor_id": actor_id,
        "role_kind": role_kind,
        "scope": actor_scope,
        "actual_model": model,
        "model_provider": "OPENAI",
        "capability_profile_id": f"CAPABILITY::{actor_id}",
        "capability_class": capability_class,
        "selection_tier": tier,
        "selection_reason": reason,
        "reasoning_effort": "xhigh",
        "capability_equivalence_id": None,
        "conversation_id": f"CONVERSATION::{actor_id}",
        "context_id": f"CONTEXT::{actor_id}",
        "workspace_id": f"WORKSPACE::{actor_id}",
        "runtime_namespace": f"RUNTIME::{actor_id}",
        "evidence_path": f"evidence/binding-{suffix}",
        "selection_evidence": evidence(f"selection-{suffix}"),
        "readiness_receipt": receipt("readiness", actor_id),
        "isolation_receipt": receipt("isolation", actor_id),
        "verification_receipt": receipt("verification", actor_id),
        "state": "ACTIVE",
        "supersedes": None,
        "superseded_by": None,
    }


def base_ledger() -> dict[str, Any]:
    actors = [
        ("SUPERVISOR-001", "SUPERVISOR", scope()),
        ("CHECKER-A", "CHECKER", scope(go_id="GO-01-A")),
        ("WORKER-A", "WORKER", scope(go_id="GO-01-A", cell_id="CELL-01-A.01")),
        ("VERIFICATION-A", "VERIFICATION", scope(go_id="GO-01-A")),
        ("CHECKER-B", "CHECKER", scope(go_id="GO-01-B")),
        ("WORKER-B", "WORKER", scope(go_id="GO-01-B", cell_id="CELL-01-B.01")),
        ("VERIFICATION-B", "VERIFICATION", scope(go_id="GO-01-B")),
        ("PATROL-RUN-001", "PATROL", scope()),
    ]
    bindings = [binding(*row) for row in actors]
    patrol = bindings[-1]
    patrol.update(
        selection_reason="DEFAULT_PATROL",
        capability_class="NON_TECHNICAL_PATROL",
    )
    return {
        "version": "2.6.0",
        "artifact_type": "MODEL_BINDING_LEDGER",
        "ledger_id": "MODEL-LEDGER-RUN-001-v1",
        "run_id": "RUN-001",
        "policy_version": "MODEL-POLICY-2.6.0",
        "required_actors": [
            {"actor_id": actor_id, "role_kind": role_kind} for actor_id, role_kind, _ in actors
        ],
        "cell_contracts": [
            {
                "contract_id": "CELL-CONTRACT-01-A.01-v1",
                "version": "1",
                "run_id": "RUN-001",
                "go_id": "GO-01-A",
                "cell_id": "CELL-01-A.01",
                "worker_id": "WORKER-A",
                "fine_grained": True,
                "risk_class": "LOW",
                "capacity_gate_result": "PASS",
                "evidence": evidence("cell-contract-01-a-01"),
            },
            {
                "contract_id": "CELL-CONTRACT-01-B.01-v1",
                "version": "1",
                "run_id": "RUN-001",
                "go_id": "GO-01-B",
                "cell_id": "CELL-01-B.01",
                "worker_id": "WORKER-B",
                "fine_grained": False,
                "risk_class": "MEDIUM",
                "capacity_gate_result": "PASS",
                "evidence": evidence("cell-contract-01-b-01"),
            },
        ],
        "capability_equivalences": [],
        "owner_authorizations": [],
        "bindings": bindings,
        "binding_changes": [],
        "binding_observations": [
            {
                "observation_id": f"OBS::{item['actor_id']}::001",
                "binding_id": item["binding_id"],
                "actor_id": item["actor_id"],
                "scope": deepcopy(item["scope"]),
                "actual_model": item["actual_model"],
                "reasoning_effort": item["reasoning_effort"],
                "evidence": evidence(f"observation-{item['actor_id'].lower()}"),
            }
            for item in bindings
        ],
    }


def write_ledger(tmp_path: Path, ledger: dict[str, Any]) -> Path:
    path = tmp_path / "model-binding-ledger.yaml"
    path.write_text(yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8")
    return path


def run_validator(tmp_path: Path, ledger: dict[str, Any], *, optimized: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable]
    if optimized:
        command.append("-O")
    command.extend([str(SCRIPT), str(write_ledger(tmp_path, ledger))])
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def assert_valid(tmp_path: Path, ledger: dict[str, Any]) -> None:
    result = run_validator(tmp_path, ledger)
    assert result.returncode == 0, result.stderr
    assert "PASS: CLK model binding policy" in result.stdout


def assert_invalid(tmp_path: Path, ledger: dict[str, Any], message: str, *, optimized: bool = False) -> None:
    result = run_validator(tmp_path, ledger, optimized=optimized)
    assert result.returncode != 0, result.stdout
    assert message.lower() in result.stderr.lower()


def find_binding(ledger: dict[str, Any], actor_id: str) -> dict[str, Any]:
    return next(item for item in ledger["bindings"] if item["actor_id"] == actor_id and item["state"] == "ACTIVE")


def find_observation(ledger: dict[str, Any], actor_id: str) -> dict[str, Any]:
    return next(item for item in ledger["binding_observations"] if item["actor_id"] == actor_id)


def select_luna(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "WORKER-A")
    item.update(
        actual_model="gpt-5.6-luna",
        selection_tier="LUNA_FINE_GRAINED",
        selection_reason="FINE_GRAINED_LOW_RISK_CELL",
        capability_class="FINE_GRAINED_EXECUTION",
    )
    find_observation(ledger, "WORKER-A")["actual_model"] = "gpt-5.6-luna"


def select_sol(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "CHECKER-A")
    item.update(
        actual_model="gpt-5.6-sol",
        selection_tier="SOL_EXCEPTIONAL",
        selection_reason="ROOT_CAUSE_DIAGNOSIS",
        capability_class="ADVANCED_DIAGNOSTIC",
    )
    find_observation(ledger, "CHECKER-A")["actual_model"] = "gpt-5.6-sol"


def switch_worker_to_sol(ledger: dict[str, Any]) -> None:
    old = find_binding(ledger, "WORKER-A")
    old["state"] = "SUPERSEDED"
    old["superseded_by"] = "BINDING::WORKER-A::002"
    new = deepcopy(old)
    new.update(
        binding_id="BINDING::WORKER-A::002",
        actual_model="gpt-5.6-sol",
        capability_class="ADVANCED_DIAGNOSTIC",
        selection_tier="SOL_EXCEPTIONAL",
        selection_reason="COMPLEX_REWORK",
        conversation_id="CONVERSATION::WORKER-A::002",
        context_id="CONTEXT::WORKER-A::002",
        workspace_id="WORKSPACE::WORKER-A::002",
        runtime_namespace="RUNTIME::WORKER-A::002",
        capability_profile_id="CAPABILITY::WORKER-A::002",
        evidence_path="evidence/binding-worker-a-002",
        selection_evidence=evidence("selection-worker-a-002"),
        readiness_receipt=receipt("readiness-002", "WORKER-A"),
        isolation_receipt=receipt("isolation-002", "WORKER-A"),
        verification_receipt=receipt("verification-002", "WORKER-A"),
        state="ACTIVE",
        supersedes=old["binding_id"],
        superseded_by=None,
    )
    ledger["bindings"].append(new)
    ledger["binding_changes"].append(
        {
            "change_id": "MODEL-CHANGE::WORKER-A::001",
            "actor_id": "WORKER-A",
            "scope": deepcopy(old["scope"]),
            "previous_binding_id": old["binding_id"],
            "new_binding_id": new["binding_id"],
            "change_reason": "COMPLEX_REWORK",
            "evidence": evidence("model-change-worker-a-001"),
        }
    )
    ledger["binding_observations"].append(
        {
            "observation_id": "OBS::WORKER-A::002",
            "binding_id": new["binding_id"],
            "actor_id": "WORKER-A",
            "scope": deepcopy(new["scope"]),
            "actual_model": new["actual_model"],
            "reasoning_effort": "xhigh",
            "evidence": evidence("observation-worker-a-002"),
        }
    )


def rebind_supervisor_reasoning(
    ledger: dict[str, Any], *, reasoning_effort: str, authorized: bool
) -> None:
    old = find_binding(ledger, "SUPERVISOR-001")
    old["state"] = "SUPERSEDED"
    old["superseded_by"] = "BINDING::SUPERVISOR-001::002"
    new = deepcopy(old)
    new.update(
        binding_id="BINDING::SUPERVISOR-001::002",
        reasoning_effort=reasoning_effort,
        conversation_id="CONVERSATION::SUPERVISOR-001::002",
        context_id="CONTEXT::SUPERVISOR-001::002",
        workspace_id="WORKSPACE::SUPERVISOR-001::002",
        runtime_namespace="RUNTIME::SUPERVISOR-001::002",
        capability_profile_id="CAPABILITY::SUPERVISOR-001::002",
        evidence_path="evidence/binding-supervisor-001-002",
        selection_evidence=evidence("selection-supervisor-001-002"),
        readiness_receipt=receipt("readiness-002", "SUPERVISOR-001"),
        isolation_receipt=receipt("isolation-002", "SUPERVISOR-001"),
        verification_receipt=receipt("verification-002", "SUPERVISOR-001"),
        state="ACTIVE",
        supersedes=old["binding_id"],
        superseded_by=None,
    )
    ledger["bindings"].append(new)
    ledger["binding_changes"].append(
        {
            "change_id": "MODEL-CHANGE::SUPERVISOR-001::001",
            "actor_id": "SUPERVISOR-001",
            "scope": deepcopy(old["scope"]),
            "previous_binding_id": old["binding_id"],
            "new_binding_id": new["binding_id"],
            "change_reason": "OWNER_AUTHORIZED_REASONING_CHANGE",
            "evidence": evidence("model-change-supervisor-001-001"),
        }
    )
    ledger["binding_observations"].append(
        {
            "observation_id": "OBS::SUPERVISOR-001::002",
            "binding_id": new["binding_id"],
            "actor_id": "SUPERVISOR-001",
            "scope": deepcopy(new["scope"]),
            "actual_model": new["actual_model"],
            "reasoning_effort": new["reasoning_effort"],
            "evidence": evidence("observation-supervisor-001-002"),
        }
    )
    if authorized:
        ledger["owner_authorizations"].append(
            {
                "authorization_id": "OWNER-AUTH::SUPERVISOR-001::ULTRA::002",
                "run_id": "RUN-001",
                "actor_id": "SUPERVISOR-001",
                "binding_id": new["binding_id"],
                "scope": deepcopy(new["scope"]),
                "reasoning_effort": "ultra",
                "evidence": evidence("owner-auth-supervisor-ultra-002"),
            }
        )


def bind_terra_equivalent(ledger: dict[str, Any], model: str) -> None:
    item = find_binding(ledger, "SUPERVISOR-001")
    item["actual_model"] = model
    item["capability_equivalence_id"] = "EQUIV-TERRA-LAUNDERING"
    find_observation(ledger, "SUPERVISOR-001")["actual_model"] = model
    ledger["capability_equivalences"].append(
        {
            "equivalence_id": "EQUIV-TERRA-LAUNDERING",
            "actual_model": model,
            "target_selection_tier": "TERRA_DEFAULT",
            "capability_class": "TECHNICAL_GENERAL",
            "result": "PROVEN_EQUIVALENT",
            "evidence": evidence("equiv-terra-laundering"),
        }
    )


def test_terra_xhigh_is_the_default_for_technical_roles_and_patrol(tmp_path: Path) -> None:
    assert_valid(tmp_path, base_ledger())


def test_fine_grained_low_risk_worker_cell_may_use_luna(tmp_path: Path) -> None:
    ledger = base_ledger()
    select_luna(ledger)
    assert_valid(tmp_path, ledger)


def test_high_complexity_diagnosis_may_use_sol(tmp_path: Path) -> None:
    ledger = base_ledger()
    select_sol(ledger)
    assert_valid(tmp_path, ledger)


def test_proven_capability_equivalent_alternative_may_replace_reference_model(tmp_path: Path) -> None:
    ledger = base_ledger()
    item = find_binding(ledger, "SUPERVISOR-001")
    item["actual_model"] = "other-frontier-terra-equivalent"
    item["model_provider"] = "OTHER"
    item["capability_equivalence_id"] = "EQUIV-TERRA-001"
    find_observation(ledger, "SUPERVISOR-001")["actual_model"] = item["actual_model"]
    ledger["capability_equivalences"].append(
        {
            "equivalence_id": "EQUIV-TERRA-001",
            "actual_model": item["actual_model"],
            "target_selection_tier": "TERRA_DEFAULT",
            "capability_class": "TECHNICAL_GENERAL",
            "result": "PROVEN_EQUIVALENT",
            "evidence": evidence("equiv-terra-001"),
        }
    )
    assert_valid(tmp_path, ledger)


def test_item_specific_owner_authorization_may_enable_ultra(tmp_path: Path) -> None:
    ledger = base_ledger()
    item = find_binding(ledger, "SUPERVISOR-001")
    item["reasoning_effort"] = "ultra"
    find_observation(ledger, "SUPERVISOR-001")["reasoning_effort"] = "ultra"
    ledger["owner_authorizations"].append(
        {
            "authorization_id": "OWNER-AUTH::SUPERVISOR-001::ULTRA::001",
            "run_id": "RUN-001",
            "actor_id": "SUPERVISOR-001",
            "binding_id": item["binding_id"],
            "scope": deepcopy(item["scope"]),
            "reasoning_effort": "ultra",
            "evidence": evidence("owner-auth-supervisor-ultra-001"),
        }
    )
    assert_valid(tmp_path, ledger)


def test_model_change_creates_a_new_verified_binding(tmp_path: Path) -> None:
    ledger = base_ledger()
    switch_worker_to_sol(ledger)
    assert_valid(tmp_path, ledger)


def test_owner_authorized_reasoning_only_rebinding_is_valid(tmp_path: Path) -> None:
    ledger = base_ledger()
    rebind_supervisor_reasoning(ledger, reasoning_effort="ultra", authorized=True)
    assert_valid(tmp_path, ledger)


@pytest.mark.parametrize(
    "snapshot_model",
    ["gpt-5.6-luna-preview", "gpt-5.6-luna.preview", "gpt-5.6-luna_snapshot"],
)
def test_same_family_luna_snapshot_requires_and_accepts_luna_equivalence(
    tmp_path: Path, snapshot_model: str
) -> None:
    ledger = base_ledger()
    select_luna(ledger)
    item = find_binding(ledger, "WORKER-A")
    item["actual_model"] = snapshot_model
    item["capability_equivalence_id"] = "EQUIV-LUNA-PREVIEW"
    find_observation(ledger, "WORKER-A")["actual_model"] = item["actual_model"]
    ledger["capability_equivalences"].append(
        {
            "equivalence_id": "EQUIV-LUNA-PREVIEW",
            "actual_model": item["actual_model"],
            "target_selection_tier": "LUNA_FINE_GRAINED",
            "capability_class": "FINE_GRAINED_EXECUTION",
            "result": "PROVEN_EQUIVALENT",
            "evidence": evidence("equiv-luna-preview"),
        }
    )
    assert_valid(tmp_path, ledger)


def test_lunar_name_is_not_misclassified_as_luna_family(tmp_path: Path) -> None:
    ledger = base_ledger()
    bind_terra_equivalent(ledger, "gpt-5.6-lunar-preview")
    assert_valid(tmp_path, ledger)


@pytest.mark.parametrize(
    ("model", "message"),
    [
        ("GPT-5.6-LUNA", "canonical lowercase"),
        ("gpt-5.6-Luna", "canonical lowercase"),
        ("gpt-5.6-luna ", "leading or trailing whitespace"),
        ("gpt-5.6-luna-preview", "Luna is Worker-only"),
        ("gpt-5.6-sol-20260806", "Sol requires exceptional"),
        ("gpt-5.6-luna.preview", "Luna is Worker-only"),
        ("gpt-5.6-sol_snapshot", "Sol requires exceptional"),
    ],
)
def test_known_gpt_family_identity_laundering_is_rejected(
    tmp_path: Path, model: str, message: str
) -> None:
    ledger = base_ledger()
    bind_terra_equivalent(ledger, model)
    assert_invalid(tmp_path, ledger, message)


@pytest.mark.parametrize(
    ("model", "message"),
    [
        ("GPT-5.6-LUNA", "canonical lowercase"),
        ("gpt-5.6-Luna", "canonical lowercase"),
        ("gpt-5.6-luna ", "leading or trailing whitespace"),
        ("gpt-5.6-luna-preview", "Luna is Worker-only"),
        ("gpt-5.6-sol-20260806", "Sol requires exceptional"),
        ("gpt-5.6-luna.preview", "Luna is Worker-only"),
        ("gpt-5.6-sol_snapshot", "Sol requires exceptional"),
    ],
)
def test_known_gpt_family_laundering_fails_under_python_optimized(
    tmp_path: Path, model: str, message: str
) -> None:
    ledger = base_ledger()
    bind_terra_equivalent(ledger, model)
    assert_invalid(tmp_path, ledger, message, optimized=True)


def mutate_gpt_55(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "SUPERVISOR-001")
    item["actual_model"] = "gpt-5.5"
    find_observation(ledger, "SUPERVISOR-001")["actual_model"] = "gpt-5.5"


def mutate_unapproved_ultra(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "SUPERVISOR-001")
    item["reasoning_effort"] = "ultra"
    find_observation(ledger, "SUPERVISOR-001")["reasoning_effort"] = "ultra"


def mutate_unjustified_luna(ledger: dict[str, Any]) -> None:
    select_luna(ledger)
    ledger["cell_contracts"][0]["fine_grained"] = False


def mutate_non_equivalent(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "SUPERVISOR-001")
    item["actual_model"] = "unknown-model"
    item["model_provider"] = "OTHER"
    item["capability_equivalence_id"] = "EQUIV-UNKNOWN"
    find_observation(ledger, "SUPERVISOR-001")["actual_model"] = "unknown-model"
    ledger["capability_equivalences"].append(
        {
            "equivalence_id": "EQUIV-UNKNOWN",
            "actual_model": "unknown-model",
            "target_selection_tier": "TERRA_DEFAULT",
            "capability_class": "TECHNICAL_GENERAL",
            "result": "UNKNOWN",
            "evidence": evidence("equiv-unknown"),
        }
    )


def mutate_ordinary_sol(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "CHECKER-A")
    item["actual_model"] = "gpt-5.6-sol"
    find_observation(ledger, "CHECKER-A")["actual_model"] = "gpt-5.6-sol"


def mutate_silent_switch(ledger: dict[str, Any]) -> None:
    find_observation(ledger, "WORKER-A")["actual_model"] = "gpt-5.6-sol"


def mutate_same_model_isolation_reuse(ledger: dict[str, Any]) -> None:
    find_binding(ledger, "VERIFICATION-A")["capability_profile_id"] = find_binding(ledger, "CHECKER-A")["capability_profile_id"]


def mutate_patrol_luna_bypass(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "PATROL-RUN-001")
    item["actual_model"] = "gpt-5.6-luna"
    find_observation(ledger, "PATROL-RUN-001")["actual_model"] = "gpt-5.6-luna"


def mutate_luna_checker_with_fake_equivalence(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "CHECKER-A")
    item["actual_model"] = "gpt-5.6-luna"
    item["capability_equivalence_id"] = "EQUIV-LUNA-AS-TERRA"
    find_observation(ledger, "CHECKER-A")["actual_model"] = "gpt-5.6-luna"
    ledger["capability_equivalences"].append(
        {
            "equivalence_id": "EQUIV-LUNA-AS-TERRA",
            "actual_model": "gpt-5.6-luna",
            "target_selection_tier": "TERRA_DEFAULT",
            "capability_class": "TECHNICAL_GENERAL",
            "result": "PROVEN_EQUIVALENT",
            "evidence": evidence("fake-luna-as-terra"),
        }
    )


def mutate_patrol_to_cell_scope(ledger: dict[str, Any]) -> None:
    item = find_binding(ledger, "PATROL-RUN-001")
    item["scope"] = scope(go_id="GO-01-A", cell_id="CELL-01-A.01")
    find_observation(ledger, "PATROL-RUN-001")["scope"] = deepcopy(item["scope"])


def mutate_role_pollution(ledger: dict[str, Any]) -> None:
    ledger["required_actors"].append({"actor_id": "ROUTER-001", "role_kind": "ROUTER"})


def mutate_single_chain_roster(ledger: dict[str, Any]) -> None:
    removed = {"CHECKER-B", "WORKER-B", "VERIFICATION-B"}
    ledger["required_actors"] = [row for row in ledger["required_actors"] if row["actor_id"] not in removed]
    ledger["bindings"] = [row for row in ledger["bindings"] if row["actor_id"] not in removed]
    ledger["binding_observations"] = [row for row in ledger["binding_observations"] if row["actor_id"] not in removed]
    ledger["cell_contracts"] = [row for row in ledger["cell_contracts"] if row["worker_id"] not in removed]


def mutate_switch_without_change_record(ledger: dict[str, Any]) -> None:
    switch_worker_to_sol(ledger)
    ledger["binding_changes"].clear()


def mutate_switch_reuses_readiness(ledger: dict[str, Any]) -> None:
    switch_worker_to_sol(ledger)
    old, new = [item for item in ledger["bindings"] if item["actor_id"] == "WORKER-A"]
    new["readiness_receipt"] = deepcopy(old["readiness_receipt"])


def mutate_reasoning_rebinding_without_owner_authorization(ledger: dict[str, Any]) -> None:
    rebind_supervisor_reasoning(ledger, reasoning_effort="ultra", authorized=False)


def mutate_noop_binding_change(ledger: dict[str, Any]) -> None:
    rebind_supervisor_reasoning(ledger, reasoning_effort="xhigh", authorized=False)


def mutate_silent_reasoning_drift(ledger: dict[str, Any]) -> None:
    find_observation(ledger, "SUPERVISOR-001")["reasoning_effort"] = "ultra"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (mutate_gpt_55, "GPT 5.5 and lower"),
        (mutate_unapproved_ultra, "Owner authorization"),
        (mutate_unjustified_luna, "fine-grained low-risk"),
        (mutate_non_equivalent, "proven equivalent"),
        (mutate_ordinary_sol, "Sol requires exceptional"),
        (mutate_silent_switch, "silent model switch"),
        (mutate_same_model_isolation_reuse, "isolation identities"),
        (mutate_patrol_luna_bypass, "patrol must use Terra"),
        (mutate_luna_checker_with_fake_equivalence, "Luna is Worker-only"),
        (mutate_patrol_to_cell_scope, "patrol binding must be Run-scoped"),
        (mutate_role_pollution, "canonical CLK roles"),
        (mutate_single_chain_roster, "at least two Checker/Worker Chains"),
        (mutate_switch_without_change_record, "explicit binding change"),
        (mutate_switch_reuses_readiness, "fresh binding receipt"),
        (mutate_reasoning_rebinding_without_owner_authorization, "Owner authorization"),
        (mutate_noop_binding_change, "actual model or reasoning effort"),
        (mutate_silent_reasoning_drift, "silent model switch"),
    ],
)
def test_invalid_model_policy_fails_closed(
    tmp_path: Path, mutation: Callable[[dict[str, Any]], None], message: str
) -> None:
    ledger = base_ledger()
    mutation(ledger)
    assert_invalid(tmp_path, ledger, message)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (mutate_gpt_55, "GPT 5.5 and lower"),
        (mutate_unapproved_ultra, "Owner authorization"),
        (mutate_unjustified_luna, "fine-grained low-risk"),
        (mutate_non_equivalent, "proven equivalent"),
        (mutate_silent_switch, "silent model switch"),
        (mutate_reasoning_rebinding_without_owner_authorization, "Owner authorization"),
        (mutate_noop_binding_change, "actual model or reasoning effort"),
        (mutate_silent_reasoning_drift, "silent model switch"),
    ],
)
def test_critical_invalid_policy_fails_closed_under_python_optimized(
    tmp_path: Path, mutation: Callable[[dict[str, Any]], None], message: str
) -> None:
    ledger = base_ledger()
    mutation(ledger)
    assert_invalid(tmp_path, ledger, message, optimized=True)
