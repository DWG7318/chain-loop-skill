from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chain-loop-skill" / "scripts" / "run_clk_readiness_eval.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("clk_eval", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_canonical_answers_pass() -> None:
    module = load_runner()
    bank = module.load_json(
        ROOT / "chain-loop-skill" / "evals" / "clk-readiness-questions.json"
    )
    key = module.load_json(
        ROOT / "chain-loop-skill" / "evals" / "clk-readiness-answer-key.json"
    )
    order = module.emit_questions(bank, 7318)
    submitted = {
        "question_order": [q["id"] for q in order],
        "answers": [{"id": q["id"], "answer": key["answers"][q["id"]]} for q in order],
    }
    passed, results = module.grade(bank, key, submitted, [q["id"] for q in order])
    assert passed
    assert all(item["passed"] for item in results)
    assert bank["version"] == "2.3.1"
    assert key["version"] == "2.3.1"
    joined = "\n".join(key["answers"].values())
    for marker in (
        "每条CHAIN最多一个ACTIVE GO",
        "D0、D1、D2、条件式LEVEL、D3",
        "formal resolution不能替代",
        "Optional GO",
        "LOOP_OWNER_ACCEPTED",
    ):
        assert marker in joined


def test_one_wrong_answer_fails() -> None:
    module = load_runner()
    bank = module.load_json(
        ROOT / "chain-loop-skill" / "evals" / "clk-readiness-questions.json"
    )
    key = module.load_json(
        ROOT / "chain-loop-skill" / "evals" / "clk-readiness-answer-key.json"
    )
    order = module.emit_questions(bank, 7318)
    answers = [{"id": q["id"], "answer": key["answers"][q["id"]]} for q in order]
    answers[0]["answer"] = "错误答案"
    passed, results = module.grade(
        bank,
        key,
        {"question_order": [q["id"] for q in order], "answers": answers},
        [q["id"] for q in order],
    )
    assert not passed
    assert sum(item["passed"] for item in results) == 24


def test_grade_rejects_non_seeded_order():
    module=load_runner()
    q=module.load_json(ROOT/'chain-loop-skill/evals/clk-readiness-questions.json')
    a=module.load_json(ROOT/'chain-loop-skill/evals/clk-readiness-answer-key.json')
    expected=[x['id'] for x in module.emit_questions(q,2000)]
    wrong=list(reversed(expected))
    submitted={'question_order':wrong,'answers':[{'id':i,'answer':a['answers'][i]} for i in wrong]}
    try:
        module.grade(q,a,submitted,expected)
    except SystemExit:
        return
    raise AssertionError('non-seeded order must fail')
