#!/usr/bin/env python3
"""Validate consumed-receipt hashes and immutable candidate continuity."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "chain-loop-skill" / "schemas" / "receipt-envelope.schema.json"
REQUIRED_PREDECESSORS = {"D1": "D0", "D2": "D1"}


class ReceiptChainValidationError(ValueError):
    """Raised when a Receipt chain is incomplete, stale, or misbound."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReceiptChainValidationError(message)


def receipt_document_hash(receipt: dict[str, Any]) -> str:
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_receipt_chain(receipts: list[dict[str, Any]]) -> None:
    require(bool(receipts), "Receipt chain must not be empty")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    by_id: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        errors = sorted(validator.iter_errors(receipt), key=lambda error: list(error.path))
        require(not errors, f"Receipt schema violation: {errors[0].message if errors else ''}")
        receipt_id = receipt["receipt_id"]
        require(receipt_id not in by_id, f"duplicate Receipt ID: {receipt_id}")
        by_id[receipt_id] = receipt

    for receipt in receipts:
        consumed_types: set[str] = set()
        for consumed_ref in receipt["consumed_receipts"]:
            consumed_id = consumed_ref["receipt_id"]
            require(consumed_id in by_id, f"consumed Receipt is missing: {consumed_id}")
            consumed = by_id[consumed_id]
            consumed_types.add(consumed["receipt_type"])
            require(consumed_ref["receipt_hash"] == receipt_document_hash(consumed),
                    f"consumed Receipt hash mismatch: {consumed_id}")
            for field in ("run_id", "feature_slice_id", "baseline_id", "baseline_version", "baseline_hash"):
                require(receipt[field] == consumed[field],
                        f"consumed Receipt {field} mismatch: {consumed_id}")
            if receipt["receipt_type"] in {"D1", "D2"}:
                require(receipt["candidate_digest"] == consumed["candidate_digest"],
                        f"candidate mismatch between {receipt['receipt_id']} and {consumed_id}")
        predecessor = REQUIRED_PREDECESSORS.get(receipt["receipt_type"])
        if predecessor:
            require(predecessor in consumed_types,
                    f"{receipt['receipt_type']} must consume at least one {predecessor} Receipt")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipts", nargs="+", type=Path)
    args = parser.parse_args(argv)
    try:
        documents = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in args.receipts]
        validate_receipt_chain(documents)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ReceiptChainValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: CLK Receipt chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
