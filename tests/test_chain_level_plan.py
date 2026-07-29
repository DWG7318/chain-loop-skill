from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_chain_level_plan.py"
FIXTURES = ROOT / "tests" / "fixtures" / "plans"


def run_validator(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / name)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_multi_chain_level_plan_passes() -> None:
    result = run_validator("valid-minimal.yaml")
    assert result.returncode == 0, result.stderr
    assert "PASS: Chain/Level plan" in result.stdout


@pytest.mark.parametrize(
    ("fixture", "message"),
    [
        ("invalid-single-chain.yaml", "at least two non-empty Chains"),
        ("invalid-duplicate-go.yaml", "GO IDs must be globally unique"),
        ("invalid-reversed-order.yaml", "does not follow frozen go_order"),
        ("invalid-duplicate-level.yaml", "Level ordinals must be unique"),
    ],
)
def test_invalid_plan_is_rejected(fixture: str, message: str) -> None:
    result = run_validator(fixture)
    assert result.returncode == 2
    assert message in result.stderr
