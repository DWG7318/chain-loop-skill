#!/usr/bin/env python3
"""Validate the complete CLK 2.3.1 repository contract."""

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
IGNORED_PARTS = {".git", ".codex", ".worktrees", ".pytest_cache", "__pycache__"}
REQUIRED_FILES = {
    ".gitattributes",
    ".github/workflows/validate.yml",
    ".gitignore",
    "CHANGELOG.md",
    "FILE_HASHES.json",
    "LICENSE",
    "MANIFEST.json",
    "MIGRATION-2.0-TO-2.3.1.md",
    "MIGRATION-MSLK-TO-CLK.md",
    "README.md",
    "SPEC.md",
    "VALIDATION-REPORT.md",
    "VERSION",
    "requirements-dev.txt",
    "scripts/update_file_hashes.py",
    "scripts/validate_chain_level_plan.py",
    "scripts/validate_receipt_chain.py",
    "scripts/validate_repository.py",
    "scripts/validate_runtime_state.py",
    "chain-loop-skill/SKILL.md",
    "chain-loop-skill/agents/openai.yaml",
    "chain-loop-skill/contracts/clk-control-kernel.json",
    "chain-loop-skill/schemas/amendment-envelope.schema.json",
    "chain-loop-skill/schemas/chain-level-plan.schema.json",
    "chain-loop-skill/schemas/receipt-envelope.schema.json",
    "chain-loop-skill/schemas/runtime-state-index.schema.json",
    "chain-loop-skill/templates/go-amendment.yaml",
    "chain-loop-skill/templates/level-barrier-receipt.yaml",
    "chain-loop-skill/templates/owner-acceptance.yaml",
}


class RepositoryValidationError(ValueError):
    """Raised when release artifacts are inconsistent or incomplete."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RepositoryValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_ignored(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return any(part in IGNORED_PARTS for part in relative.parts) or path.suffix in {".pyc", ".log", ".tmp"}


def release_files(root: Path) -> list[Path]:
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and not is_ignored(path, root)
        and path.relative_to(root).as_posix() != "FILE_HASHES.json"
    ]
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def validate_required_files(root: Path) -> None:
    missing = sorted(path for path in REQUIRED_FILES if not (root / path).is_file())
    require(not missing, f"missing required files: {missing}")


def validate_skill_frontmatter(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    require(lines and lines[0] == "---", f"{path.name} frontmatter is missing")
    try:
        end = lines[1:].index("---") + 1
    except ValueError as error:
        raise RepositoryValidationError(f"{path.name} frontmatter is not closed") from error
    metadata = yaml.safe_load("\n".join(lines[1:end]))
    require(isinstance(metadata, dict), f"{path.name} frontmatter must be a mapping")
    require(metadata.get("name") == "chain-loop-skill", "Skill frontmatter name must be chain-loop-skill")
    require(isinstance(metadata.get("description"), str) and bool(metadata["description"].strip()),
            "Skill frontmatter description must be non-empty")


def validate_version_consistency(root: Path) -> None:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    require(version == "2.3.1", f"VERSION must be 2.3.1, got {version}")
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    require(manifest.get("version") == version, "MANIFEST version differs from VERSION")
    readme = (root / "README.md").read_text(encoding="utf-8")
    require(f"Current version: **{version}**" in readme, "README version differs from VERSION")
    spec = (root / "SPEC.md").read_text(encoding="utf-8")
    require(version in spec.splitlines()[0], "SPEC version differs from VERSION")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    require(f"## {version}" in changelog, "CHANGELOG version differs from VERSION")
    skill = (root / "chain-loop-skill" / "SKILL.md").read_text(encoding="utf-8")
    require(f"Current specification version: `{version}`." in skill,
            "canonical Skill version differs from VERSION")
    control = json.loads(
        (root / "chain-loop-skill" / "contracts" / "clk-control-kernel.json").read_text(encoding="utf-8")
    )
    require(control.get("version") == version and control.get("schema_version") == version,
            "control-kernel version differs from VERSION")
    run_receipt = yaml.safe_load(
        (root / "chain-loop-skill" / "templates" / "clk-run-receipt.yaml").read_text(encoding="utf-8")
    )
    require(str(run_receipt.get("version")) == version, "Run Receipt version differs from VERSION")
    for name in ("clk-readiness-questions.json", "clk-readiness-answer-key.json"):
        readiness = json.loads(
            (root / "chain-loop-skill" / "evals" / name).read_text(encoding="utf-8")
        )
        require(readiness.get("version") == version, f"{name} version differs from VERSION")


def parse_structured_files(root: Path) -> None:
    for path in release_files(root):
        try:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as error:
            raise RepositoryValidationError(
                f"structured file {path.relative_to(root).as_posix()} is invalid: {error}"
            ) from error


def validate_hash_manifest(root: Path, *, require_complete: bool = True) -> None:
    hash_path = root / "FILE_HASHES.json"
    hashes = json.loads(hash_path.read_text(encoding="utf-8"))
    require(isinstance(hashes, dict), "FILE_HASHES.json must be an object")
    for relative, expected in hashes.items():
        path = root / relative
        require(path.is_file(), f"hash manifest references missing file: {relative}")
        actual = sha256(path)
        require(actual == expected, f"hash mismatch: {relative}")
    if require_complete:
        expected_paths = {path.relative_to(root).as_posix() for path in release_files(root)}
        require(set(hashes) == expected_paths,
                f"hash manifest coverage mismatch: {sorted(set(hashes) ^ expected_paths)}")


def validate_markdown_budgets(root: Path) -> None:
    for path in release_files(root):
        if path.suffix.lower() != ".md":
            continue
        count = len(path.read_text(encoding="utf-8").splitlines())
        require(count <= 1000, f"Markdown line budget exceeded: {path.relative_to(root)} ({count})")
        if path.name.lower() == "work-continuation-index.md":
            require(count < 200, f"WORK_CONTINUATION_INDEX exceeds 200 lines: {path.relative_to(root)}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name} must contain a mapping")
    return value


def validate_templates(root: Path) -> None:
    schemas = root / "chain-loop-skill" / "schemas"
    templates = root / "chain-loop-skill" / "templates"
    pairs = [
        ("chain-level-plan.schema.json", "chain-level-plan.yaml"),
        ("runtime-state-index.schema.json", "runtime-state-index.yaml"),
    ]
    receipt_names = [
        "d0-worker-receipt.yaml",
        "d1-checker-receipt.yaml",
        "d2-go-verification-receipt.yaml",
        "level-verification-receipt.yaml",
        "d3-run-verification-receipt.yaml",
    ]
    amendment_names = ["chain-amendment.yaml", "level-amendment.yaml", "go-amendment.yaml"]
    pairs.extend(("receipt-envelope.schema.json", name) for name in receipt_names)
    pairs.extend(("amendment-envelope.schema.json", name) for name in amendment_names)
    for schema_name, template_name in pairs:
        errors = sorted(
            Draft202012Validator(load_json(schemas / schema_name)).iter_errors(load_yaml(templates / template_name)),
            key=lambda error: list(error.path),
        )
        require(not errors, f"template {template_name} violates {schema_name}: {errors[0].message if errors else ''}")


def validate_manifest(root: Path) -> None:
    manifest = load_json(root / "MANIFEST.json")
    require(manifest.get("name") == "Chain Loop Skill", "MANIFEST canonical name is invalid")
    require(manifest.get("abbreviation") == "CLK", "MANIFEST abbreviation is invalid")
    require(manifest.get("synchronization_unit") == "LEVEL", "MANIFEST must keep Level canonical")
    require(manifest.get("repository_id") == 1298120736, "MANIFEST repository ID is invalid")
    declared = set(manifest.get("required_files", []))
    require(REQUIRED_FILES <= declared, "MANIFEST required_files is incomplete")


def validate_repository(root: Path) -> None:
    validate_required_files(root)
    validate_skill_frontmatter(root / "chain-loop-skill" / "SKILL.md")
    validate_version_consistency(root)
    parse_structured_files(root)
    validate_manifest(root)
    validate_templates(root)
    validate_markdown_budgets(root)
    validate_hash_manifest(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        validate_repository(args.root.resolve())
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError, RepositoryValidationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: CLK repository 2.3.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
