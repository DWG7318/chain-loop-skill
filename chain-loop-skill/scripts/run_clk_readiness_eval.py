#!/usr/bin/env python3
"""Run or grade the CLK 2.6.0 readiness evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any


ROLE_TYPES = {"SUPERVISOR", "CHECKER", "WORKER", "VERIFICATION"}


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def normalize(value: str) -> str:
    return " ".join(value.strip().split()).casefold()


def content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit_questions(bank: dict[str, Any], seed: int) -> list[dict[str, str]]:
    questions = list(bank["questions"])
    rng = random.Random(seed)
    rng.shuffle(questions)
    return questions


def grade(
    bank: dict[str, Any],
    key: dict[str, Any],
    submitted: dict[str, Any],
    expected_order: list[str],
) -> tuple[bool, list[dict[str, Any]]]:
    expected_ids = [item["id"] for item in bank["questions"]]
    supplied = submitted.get("answers")
    if not isinstance(supplied, list):
        raise SystemExit("answers file must contain an 'answers' list")

    if submitted.get("question_order") != expected_order:
        raise SystemExit("question_order does not match the seeded evaluation order")

    if [item.get("id") for item in supplied] != expected_order:
        raise SystemExit("answers order must exactly match the seeded question_order")

    if sorted(item.get("id") for item in supplied) != sorted(expected_ids):
        raise SystemExit("answers must contain every question exactly once")

    results: list[dict[str, Any]] = []
    all_passed = True
    for item in supplied:
        qid = item["id"]
        actual = str(item.get("answer", ""))
        expected = str(key["answers"][qid])
        passed = normalize(actual) == normalize(expected)
        all_passed = all_passed and passed
        results.append({"id": qid, "passed": passed})
    return all_passed, results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, choices=sorted(ROLE_TYPES))
    parser.add_argument("--role-id", required=True)
    parser.add_argument("--conversation-id", required=True)
    parser.add_argument("--context-id", required=True)
    parser.add_argument("--model-binding-id", required=True)
    parser.add_argument("--pair-id-or-go-id", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()

    base = Path(__file__).resolve().parents[1]
    bank_path = base / "evals" / "clk-readiness-questions.json"
    key_path = base / "evals" / "clk-readiness-answer-key.json"
    bank = load_json(bank_path)
    key = load_json(key_path)

    order = emit_questions(bank, args.seed)

    if args.emit:
        payload = {
            "version": bank["version"],
            "role": args.role,
            "seed": args.seed,
            "question_order": [q["id"] for q in order],
            "questions": order,
        }
        args.emit.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if not args.answers:
        if args.emit:
            return 0
        raise SystemExit("provide --emit, --answers, or both")

    submitted = load_json(args.answers)
    passed, per_question = grade(bank, key, submitted, [q["id"] for q in order])

    receipt = {
        "receipt_type": "CLK_READINESS_EVAL_PASS" if passed else "CLK_READINESS_EVAL_FAIL",
        "skill_version": bank["version"],
        "question_bank_hash": content_hash(bank_path),
        "answer_key_hash": content_hash(key_path),
        "role": args.role,
        "role_id": args.role_id,
        "pair_id_or_go_id": args.pair_id_or_go_id,
        "conversation_id": args.conversation_id,
        "context_id": args.context_id,
        "model_binding_id": args.model_binding_id,
        "seed": args.seed,
        "attempt": args.attempt,
        "score": f"{sum(r['passed'] for r in per_question)}/25",
        "per_question": per_question,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
