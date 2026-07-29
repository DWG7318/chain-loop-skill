from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_repository.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("clk_repository_validator", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_complete_repository_passes_release_validator() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS: CLK repository 2.3.1" in result.stdout


def test_missing_skill_frontmatter_is_rejected(tmp_path: Path) -> None:
    module = load_validator()
    skill = tmp_path / "SKILL.md"
    skill.write_text("# Missing frontmatter\n", encoding="utf-8")
    with pytest.raises(module.RepositoryValidationError, match="frontmatter"):
        module.validate_skill_frontmatter(skill)


def test_version_drift_is_rejected(tmp_path: Path) -> None:
    module = load_validator()
    (tmp_path / "chain-loop-skill" / "contracts").mkdir(parents=True)
    (tmp_path / "chain-loop-skill" / "templates").mkdir(parents=True)
    (tmp_path / "VERSION").write_text("2.3.1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("Current version: **2.3.0**\n", encoding="utf-8")
    (tmp_path / "SPEC.md").write_text("# Specification 2.3.1\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("## 2.3.1\n", encoding="utf-8")
    (tmp_path / "MANIFEST.json").write_text('{"version":"2.3.1"}', encoding="utf-8")
    (tmp_path / "chain-loop-skill" / "SKILL.md").write_text(
        "---\nname: chain-loop-skill\ndescription: test\n---\nCurrent specification version: `2.3.1`.\n",
        encoding="utf-8",
    )
    (tmp_path / "chain-loop-skill" / "contracts" / "clk-control-kernel.json").write_text(
        '{"version":"2.3.1","schema_version":"2.3.1"}', encoding="utf-8"
    )
    (tmp_path / "chain-loop-skill" / "templates" / "clk-run-receipt.yaml").write_text(
        "version: 2.3.1\n", encoding="utf-8"
    )
    with pytest.raises(module.RepositoryValidationError, match="README"):
        module.validate_version_consistency(tmp_path)


def test_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    module = load_validator()
    payload = tmp_path / "payload.txt"
    payload.write_text("actual", encoding="utf-8")
    wrong = hashlib.sha256(b"different").hexdigest()
    (tmp_path / "FILE_HASHES.json").write_text(
        json.dumps({"payload.txt": wrong}), encoding="utf-8"
    )
    with pytest.raises(module.RepositoryValidationError, match="hash mismatch"):
        module.validate_hash_manifest(tmp_path, require_complete=False)


def test_malformed_yaml_is_rejected(tmp_path: Path) -> None:
    module = load_validator()
    (tmp_path / "broken.yaml").write_text("items: [unterminated\n", encoding="utf-8")
    with pytest.raises(module.RepositoryValidationError, match="broken.yaml"):
        module.parse_structured_files(tmp_path)


def test_required_go_amendment_and_ci_assets_are_present() -> None:
    module = load_validator()
    module.validate_required_files(ROOT)
    assert (ROOT / "chain-loop-skill" / "templates" / "go-amendment.yaml").is_file()
    assert (ROOT / ".github" / "workflows" / "validate.yml").is_file()
    assert (ROOT / "requirements-dev.txt").is_file()


def test_ci_pip_cache_uses_the_declared_dependency_file() -> None:
    workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert "cache: pip" in workflow
    assert "cache-dependency-path: requirements-dev.txt" in workflow
