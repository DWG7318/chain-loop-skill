from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".codex", ".worktrees", "__pycache__", ".pytest_cache"}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def release_paths() -> set[str]:
    values: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if relative.as_posix() == "MANIFEST.json" or path.suffix == ".pyc":
            continue
        values.add(relative.as_posix())
    return values


def load_repository_validator():
    path = ROOT / "scripts" / "validate_repository.py"
    spec = importlib.util.spec_from_file_location("clk_validate_repository", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_inventory_ignores_environment_owned_worktrees(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("release\n", encoding="utf-8")
    nested = tmp_path / ".worktrees" / "old-candidate" / "README.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("external\n", encoding="utf-8")

    module = load_repository_validator()
    assert [path.as_posix() for path in module.release_files(tmp_path)] == [
        "README.md"
    ]


def test_repository_validator_passes_for_the_300_collection() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_repository.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: CLK 3.0 skill collection" in result.stdout


def test_manifest_exactly_covers_repository_bytes_except_itself() -> None:
    manifest = json.loads(read("MANIFEST.json"))
    listed = {item["path"]: item["sha256"] for item in manifest["files"]}
    assert manifest == {
        "name": "Chain Loop Skill Collection",
        "version": "3.0.0",
        "skill_count": 9,
        "excludes": ["MANIFEST.json"],
        "files": manifest["files"],
    }
    assert set(listed) == release_paths()
    for relative, digest in listed.items():
        assert sha256(ROOT / relative) == digest, relative


def test_readmes_explain_the_clk_topology_and_collection_shape() -> None:
    english = read("README.md")
    chinese = read("README.zh-CN.md")
    for text in (english, chinese):
        assert "3.0.0" in text
        assert "9" in text
        assert "skills/chain-loop-skill/SKILL.md" in text
        assert "Supervisor" in text
        assert "Checker" in text
        assert "Worker" in text
        assert "Fusion" in text
        assert "Owner" in text
        assert "SLK" in text
    assert "2+ concurrent SLK construction Chains" in english
    assert "complete fusion interface contracts" in english
    assert "temporary physical isolation" in english
    assert "两条或以上并行的 SLK 施工 Chain" in chinese
    assert "完整融合接口合同" in chinese
    assert "临时物理隔离" in chinese


def test_migration_changelog_and_validation_report_state_verified_boundaries() -> None:
    migration = read("MIGRATION.md")
    changelog = read("CHANGELOG.md")
    report = read("VALIDATION-REPORT.md")
    assert "2.6.0" in migration and "3.0.0" in migration
    assert "不保留第二套活跃内核" in migration
    assert "## 3.0.0" in changelog
    assert "remote release" in report.lower()
    assert "pending" in report.lower()
    assert "global installation" in report.lower()


def test_ci_runs_repository_collection_and_pytest_on_windows_and_ubuntu() -> None:
    workflow = read(".github/workflows/validate.yml")
    assert "ubuntu-latest" in workflow
    assert "windows-latest" in workflow
    assert "python -m pip install pytest" in workflow
    assert "python scripts/validate_repository.py" in workflow
    assert "python scripts/quick_validate.py skills" in workflow
    assert "python -m pytest -q" in workflow
    assert "validate_runtime_state.py" not in workflow


def test_required_assets_license_and_lf_policy_are_present() -> None:
    required = (
        "skills/chain-loop-skill/assets/CLK-RUN.template.md",
        "skills/clk-design-fusion-contracts/assets/FUSION-INTERFACE-CONTRACT.template.md",
        "skills/clk-plan-parallel-isolation/assets/PARALLEL-ISOLATION-PLAN.template.md",
    )
    for relative in required:
        assert (ROOT / relative).is_file(), relative
    assert "The above copyright notice and this permission notice" in read("LICENSE")
    assert "* text=auto eol=lf" in read(".gitattributes")
    for path in (ROOT / "skills").rglob("*"):
        if path.is_file():
            assert b"\r\n" not in path.read_bytes(), path


def test_release_text_inventory_is_utf8_and_lf_only() -> None:
    text_suffixes = {".json", ".md", ".py", ".yaml", ".yml"}
    for relative in release_paths():
        path = ROOT / relative
        if path.suffix.lower() not in text_suffixes:
            continue
        data = path.read_bytes()
        data.decode("utf-8")
        assert b"\r\n" not in data, relative


def test_clk_2x_active_kernel_is_retired_after_300_replacement() -> None:
    retired_paths = (
        "SKILL.md",
        "SPEC.md",
        "FILE_HASHES.json",
        "requirements-dev.txt",
        "POST-MERGE-RENAME.md",
        "chain-loop-skill",
        "agents",
        "contracts",
        "evals",
        "references",
        "docs/specs",
        "MIGRATION-2.0-TO-2.3.1.md",
        "MIGRATION-2.3.1-TO-2.4.0.md",
        "MIGRATION-2.4.0-TO-2.5.0.md",
        "MIGRATION-2.5.0-TO-2.6.0.md",
        "MIGRATION-MSLK-TO-CLK.md",
    )
    for relative in retired_paths:
        target = ROOT / relative
        if target.is_dir():
            active = [
                path
                for path in target.rglob("*")
                if path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ]
            assert active == [], relative
        else:
            assert not target.exists(), relative

    assert {path.name for path in (ROOT / "scripts").iterdir() if path.is_file()} == {
        "quick_validate.py",
        "validate_repository.py",
    }
    assert {path.name for path in (ROOT / "tests").iterdir() if path.is_file()} == {
        "skill_testkit.py",
        "test_repository_300.py",
        "test_skill_collection_300.py",
    }
    assert {path.name for path in ROOT.glob("MIGRATION*.md")} == {"MIGRATION.md"}
