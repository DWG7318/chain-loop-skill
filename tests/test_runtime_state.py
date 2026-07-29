from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_runtime_state.py"
FIXTURES = ROOT / "tests" / "fixtures" / "runtime"


def run_validator(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / name)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_runtime_state_passes() -> None:
    result = run_validator("valid-level-active.yaml")
    assert result.returncode == 0, result.stderr
    assert "PASS: CLK runtime state" in result.stdout


@pytest.mark.parametrize(
    ("fixture", "message"),
    [
        ("invalid-two-active-levels.yaml", "exactly one open Level"),
        ("invalid-two-active-go-same-chain.yaml", "at most one ACTIVE GO per Chain"),
        ("invalid-optional-pending-at-barrier.yaml", "Optional GO must reach a non-active terminal state"),
        ("invalid-required-formal-resolution.yaml", "Required GO requires D2_PASS"),
        ("invalid-missing-required-assignment.yaml", "Barrier assignment coverage mismatch"),
        ("invalid-reused-verification-context.yaml", "verification attempt IDs must be unique"),
    ],
)
def test_invalid_runtime_state_is_rejected(fixture: str, message: str) -> None:
    result = run_validator(fixture)
    assert result.returncode == 2
    assert message in result.stderr
