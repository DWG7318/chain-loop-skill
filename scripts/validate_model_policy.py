#!/usr/bin/env python3
"""Validate a CLK 2.6.0 MODEL_BINDING_LEDGER."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "chain-loop-skill" / "schemas" / "model-binding-ledger.schema.json"
TECHNICAL_ROLES = {"SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"}
ALL_ROLES = TECHNICAL_ROLES | {"PATROL"}
REFERENCE_MODELS = {
    "TERRA_DEFAULT": "gpt-5.6-terra",
    "LUNA_FINE_GRAINED": "gpt-5.6-luna",
    "SOL_EXCEPTIONAL": "gpt-5.6-sol",
}
REFERENCE_FAMILIES = {
    "TERRA_DEFAULT": "terra",
    "LUNA_FINE_GRAINED": "luna",
    "SOL_EXCEPTIONAL": "sol",
}
SOL_REASONS = {"HIGH_COMPLEXITY_CORRECTION", "ROOT_CAUSE_DIAGNOSIS", "COMPLEX_REWORK"}
GPT_VERSION = re.compile(r"^gpt-(\d+)\.(\d+)(?:-|$)")
GPT_FAMILY = re.compile(
    r"^gpt-(\d+)\.(\d+)-(terra|luna|sol)(?:$|-[a-z0-9][a-z0-9._-]*$)"
)


class ModelPolicyValidationError(ValueError):
    """Raised when a model binding violates CLK policy."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ModelPolicyValidationError(message)


def unique(values: list[Any], message: str) -> None:
    require(len(values) == len(set(values)), message)


def scope_key(scope: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(scope[name] for name in ("run_id", "go_id", "cell_id", "round_id"))


def validate_schema(ledger: Any) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(ledger), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(item) for item in error.path) or "<root>"
        raise ModelPolicyValidationError(f"model policy schema at {location}: {error.message}")


def validate_actor_roster(ledger: dict[str, Any]) -> dict[str, str]:
    rows = ledger["required_actors"]
    unique([row["actor_id"] for row in rows], "required actor IDs must be unique")
    require(all(row["role_kind"] in ALL_ROLES for row in rows), "required actors must use canonical CLK roles or the separate PATROL")
    counts = Counter(row["role_kind"] for row in rows)
    require(counts["SUPERVISOR"] == 1, "exactly one Supervisor is required")
    require(counts["PATROL"] == 1, "exactly one separate PATROL is required")
    require(
        counts["CHECKER"] >= 2 and counts["WORKER"] >= 2 and counts["VERIFICATION"] >= 2,
        "a Run ledger requires at least two Checker/Worker Chains and their Verification bindings",
    )
    require(counts["CHECKER"] == counts["WORKER"], "Checker and Worker binding rosters must remain paired")
    return {row["actor_id"]: row["role_kind"] for row in rows}


def validate_cell_contracts(ledger: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    rows = ledger["cell_contracts"]
    unique([row["contract_id"] for row in rows], "CELL contract IDs must be unique")
    result: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        require(row["run_id"] == ledger["run_id"], "CELL contract Run identity mismatch")
        key = (row["run_id"], row["go_id"], row["cell_id"], row["worker_id"])
        require(key not in result, "current CELL contract identity must be unique")
        result[key] = row
    return result


def validate_equivalences(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = ledger["capability_equivalences"]
    unique([row["equivalence_id"] for row in rows], "capability equivalence IDs must be unique")
    return {row["equivalence_id"]: row for row in rows}


def validate_binding_shape(
    ledger: dict[str, Any], actors: dict[str, str]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    rows = ledger["bindings"]
    unique([row["binding_id"] for row in rows], "model binding IDs must be unique")
    isolation_fields = (
        "conversation_id", "context_id", "workspace_id", "runtime_namespace",
        "capability_profile_id", "evidence_path"
    )
    for field in isolation_fields:
        unique([row[field] for row in rows], "same-model role isolation identities must remain distinct")
    receipt_ids: list[str] = []
    receipt_paths: list[str] = []
    for row in rows:
        require(row["actor_id"] in actors, "binding actor must exist in the frozen actor roster")
        require(row["role_kind"] == actors[row["actor_id"]], "binding role must match the frozen actor roster")
        require(row["scope"]["run_id"] == ledger["run_id"], "binding scope Run identity mismatch")
        for field in ("readiness_receipt", "isolation_receipt", "verification_receipt"):
            receipt = row[field]
            require(receipt["status"] == "PASS", "every binding must pass readiness, isolation, and verification")
            receipt_ids.append(receipt["receipt_id"])
            receipt_paths.append(receipt["path"])
    unique(receipt_ids, "fresh binding receipt identities must be unique")
    unique(receipt_paths, "fresh binding receipt evidence paths must be unique")
    unique(
        [row["selection_evidence"]["path"] for row in rows],
        "fresh model-selection evidence paths must be unique",
    )
    active: dict[str, dict[str, Any]] = {}
    for actor_id in actors:
        matches = [row for row in rows if row["actor_id"] == actor_id and row["state"] == "ACTIVE"]
        require(len(matches) == 1, "every required actor must have exactly one ACTIVE model binding")
        active[actor_id] = matches[0]
    require(set(active) == set(actors), "ACTIVE bindings must exactly cover the frozen actor roster")
    return {row["binding_id"]: row for row in rows}, active


def classify_gpt_model(model: str) -> str | None:
    if model.strip().casefold().startswith("gpt-"):
        require(model == model.strip(), "GPT model ID must have no leading or trailing whitespace")
        require(model == model.lower(), "GPT model ID must use canonical lowercase")
    match = GPT_VERSION.match(model)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        require((major, minor) > (5, 5), "GPT 5.5 and lower are prohibited")
    family = GPT_FAMILY.fullmatch(model)
    return family.group(3) if family else None


def validate_tier(
    binding: dict[str, Any],
    cell_contracts: dict[tuple[str, str, str, str], dict[str, Any]],
    equivalences: dict[str, dict[str, Any]],
) -> None:
    role = binding["role_kind"]
    model = binding["actual_model"]
    tier = binding["selection_tier"]
    reason = binding["selection_reason"]
    capability_class = binding["capability_class"]
    gpt_family = classify_gpt_model(model)

    if gpt_family == "sol" and reason not in SOL_REASONS:
        raise ModelPolicyValidationError("Sol requires exceptional correction, root-cause, or complex rework evidence")
    if role == "PATROL" and gpt_family == "luna":
        raise ModelPolicyValidationError("patrol must use Terra or a proven equivalent; no implicit Luna exception exists")
    if gpt_family == "luna" and not (role == "WORKER" and reason == "FINE_GRAINED_LOW_RISK_CELL"):
        raise ModelPolicyValidationError("Luna is Worker-only and requires fine-grained low-risk CELL evidence")

    if reason == "DEFAULT_PATROL":
        require(role == "PATROL", "DEFAULT_PATROL is reserved for the separate patrol")
        require(
            all(binding["scope"][field] is None for field in ("go_id", "cell_id", "round_id")),
            "patrol binding must be Run-scoped",
        )
        expected = ("TERRA_DEFAULT", "NON_TECHNICAL_PATROL")
    elif reason == "DEFAULT_TECHNICAL":
        require(role in TECHNICAL_ROLES, "DEFAULT_TECHNICAL is reserved for canonical technical roles")
        expected = ("TERRA_DEFAULT", "TECHNICAL_GENERAL")
    elif reason == "FINE_GRAINED_LOW_RISK_CELL":
        require(role == "WORKER", "Luna fine-grained selection is Worker-only")
        expected = ("LUNA_FINE_GRAINED", "FINE_GRAINED_EXECUTION")
        scope = binding["scope"]
        require(scope["go_id"] is not None and scope["cell_id"] is not None, "Luna requires a bound CELL scope")
        contract = cell_contracts.get((scope["run_id"], scope["go_id"], scope["cell_id"], binding["actor_id"]))
        require(contract is not None, "Luna requires the current versioned CELL contract")
        require(
            contract["fine_grained"] is True
            and contract["risk_class"] == "LOW"
            and contract["capacity_gate_result"] == "PASS",
            "Luna requires a fine-grained low-risk CELL with capacity PASS",
        )
    elif reason in SOL_REASONS:
        require(role in TECHNICAL_ROLES, "Sol exceptional selection is limited to technical roles")
        expected = ("SOL_EXCEPTIONAL", "ADVANCED_DIAGNOSTIC")
    else:  # schema currently closes this, retained for fail-closed future changes
        raise ModelPolicyValidationError("unknown model selection reason")

    require((tier, capability_class) == expected, "selection tier, reason, and capability class must agree")
    reference = REFERENCE_MODELS[tier]
    require(
        gpt_family is None or gpt_family == REFERENCE_FAMILIES[tier],
        "GPT model family must match the selected tier and capability class",
    )
    equivalence_id = binding["capability_equivalence_id"]
    if model == reference:
        require(equivalence_id is None, "reference model binding must not claim substitute equivalence")
        return
    require(equivalence_id is not None, "non-reference model requires proven equivalent capability evidence")
    equivalence = equivalences.get(equivalence_id)
    require(equivalence is not None, "non-reference model requires proven equivalent capability evidence")
    require(
        equivalence["actual_model"] == model
        and equivalence["target_selection_tier"] == tier
        and equivalence["capability_class"] == capability_class
        and equivalence["result"] == "PROVEN_EQUIVALENT",
        "substitute model must be proven equivalent to the selected capability tier",
    )


def validate_reasoning(ledger: dict[str, Any], bindings: dict[str, dict[str, Any]]) -> None:
    authorizations = ledger["owner_authorizations"]
    unique([row["authorization_id"] for row in authorizations], "Owner authorization IDs must be unique")
    authorization_by_binding = defaultdict(list)
    for row in authorizations:
        authorization_by_binding[row["binding_id"]].append(row)
    for binding in bindings.values():
        rows = authorization_by_binding.get(binding["binding_id"], [])
        if binding["reasoning_effort"] == "ultra":
            require(len(rows) == 1, "ultra requires one item-specific Owner authorization")
            auth = rows[0]
            require(
                auth["run_id"] == ledger["run_id"]
                and auth["actor_id"] == binding["actor_id"]
                and auth["scope"] == binding["scope"],
                "ultra Owner authorization must bind Run, actor, and exact scope",
            )
        else:
            require(not rows, "Owner ultra authorization must not be attached to an xhigh binding")
    require(
        set(authorization_by_binding) <= set(bindings),
        "Owner authorization must reference an existing binding",
    )


def validate_changes(ledger: dict[str, Any], bindings: dict[str, dict[str, Any]]) -> None:
    changes = ledger["binding_changes"]
    unique([row["change_id"] for row in changes], "model binding change IDs must be unique")
    pairs: dict[tuple[str, str], dict[str, Any]] = {}
    for row in changes:
        pair = (row["previous_binding_id"], row["new_binding_id"])
        require(pair not in pairs, "model binding change pair must be unique")
        old = bindings.get(pair[0])
        new = bindings.get(pair[1])
        require(old is not None and new is not None, "model binding change must reference existing bindings")
        require(old["state"] == "SUPERSEDED" and new["state"] == "ACTIVE", "model change must close old and activate new binding")
        require(old["superseded_by"] == new["binding_id"] and new["supersedes"] == old["binding_id"], "model change links must be reciprocal")
        require(old["actor_id"] == new["actor_id"] == row["actor_id"], "model change actor identity mismatch")
        require(old["scope"] == new["scope"] == row["scope"], "model change scope identity mismatch")
        require(
            old["actual_model"] != new["actual_model"]
            or old["reasoning_effort"] != new["reasoning_effort"],
            "model binding change must change actual model or reasoning effort",
        )
        pairs[pair] = row
    for binding in bindings.values():
        if binding["state"] == "SUPERSEDED":
            require(binding["superseded_by"] is not None, "SUPERSEDED binding must name its replacement")
            require((binding["binding_id"], binding["superseded_by"]) in pairs, "model switch requires an explicit binding change")
        else:
            require(binding["superseded_by"] is None, "ACTIVE binding cannot be superseded")
            if binding["supersedes"] is not None:
                require((binding["supersedes"], binding["binding_id"]) in pairs, "new binding must have an explicit reciprocal change")


def validate_observations(ledger: dict[str, Any], bindings: dict[str, dict[str, Any]]) -> None:
    observations = ledger["binding_observations"]
    unique([row["observation_id"] for row in observations], "model observation IDs must be unique")
    counts = Counter(row["binding_id"] for row in observations)
    for row in observations:
        binding = bindings.get(row["binding_id"])
        require(binding is not None, "model observation must reference an existing binding")
        require(
            row["actor_id"] == binding["actor_id"]
            and row["scope"] == binding["scope"]
            and row["actual_model"] == binding["actual_model"]
            and row["reasoning_effort"] == binding["reasoning_effort"],
            "silent model switch or binding identity drift is forbidden",
        )
    for binding in bindings.values():
        if binding["state"] == "ACTIVE":
            require(counts[binding["binding_id"]] == 1, "every ACTIVE binding requires exactly one current observation")


def validate_model_policy(ledger: dict[str, Any]) -> None:
    validate_schema(ledger)
    actors = validate_actor_roster(ledger)
    cell_contracts = validate_cell_contracts(ledger)
    equivalences = validate_equivalences(ledger)
    bindings, active = validate_binding_shape(ledger, actors)
    for binding in bindings.values():
        validate_tier(binding, cell_contracts, equivalences)
    validate_reasoning(ledger, bindings)
    validate_changes(ledger, bindings)
    validate_observations(ledger, bindings)
    require(
        all(active[actor]["role_kind"] == role for actor, role in actors.items()),
        "ACTIVE binding role coverage mismatch",
    )


def load_ledger(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "model binding ledger must be a mapping")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args(argv)
    try:
        validate_model_policy(load_ledger(args.ledger))
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError, ModelPolicyValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: CLK model binding policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
