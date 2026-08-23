from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
VERSION = "3.0.0"
COLLECTION_NAME = "Chain Loop Skill Collection"
EXPECTED_SKILLS = (
    "chain-loop-skill",
    "clk-plan-run",
    "clk-design-fusion-contracts",
    "clk-plan-parallel-isolation",
    "clk-grill-supervisor",
    "clk-launch-chains",
    "clk-complete-chain",
    "clk-start-fusion",
    "clk-close-run",
)
EXCLUDED_DIRS = {
    ".git",
    ".codex",
    ".worktrees",
    "__pycache__",
    ".pytest_cache",
}
EXCLUDED_FILES = {"MANIFEST.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def release_files(root: Path) -> list[Path]:
    values: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if relative.as_posix() in EXCLUDED_FILES or path.suffix == ".pyc":
            continue
        values.append(relative)
    return sorted(values, key=lambda item: item.as_posix())


def manifest_payload(root: Path) -> dict:
    return {
        "name": COLLECTION_NAME,
        "version": VERSION,
        "skill_count": len(EXPECTED_SKILLS),
        "excludes": sorted(EXCLUDED_FILES),
        "files": [
            {"path": relative.as_posix(), "sha256": sha256(root / relative)}
            for relative in release_files(root)
        ],
    }


def write_manifest(root: Path) -> None:
    text = json.dumps(manifest_payload(root), ensure_ascii=False, indent=2) + "\n"
    (root / "MANIFEST.json").write_bytes(text.encode("utf-8"))


def check(condition: bool, code: str, detail: str, errors: list[str]) -> None:
    if not condition:
        errors.append(f"{code}: {detail}")


def utf8_lf_text(path: Path, errors: list[str]) -> str:
    try:
        data = path.read_bytes()
        if b"\r\n" in data:
            errors.append(f"CLK_REPO_LF: {path.relative_to(ROOT).as_posix()}")
        return data.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"CLK_REPO_UTF8: {path}: {exc}")
        return ""


def frontmatter_name(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = (
        "VERSION",
        "README.md",
        "README.zh-CN.md",
        "MIGRATION.md",
        "CHANGELOG.md",
        "LICENSE",
        "MANIFEST.json",
        "VALIDATION-REPORT.md",
        ".github/workflows/validate.yml",
        "skills/chain-loop-skill/assets/CLK-RUN.template.md",
        "skills/clk-design-fusion-contracts/assets/FUSION-INTERFACE-CONTRACT.template.md",
        "skills/clk-plan-parallel-isolation/assets/PARALLEL-ISOLATION-PLAN.template.md",
    )
    for relative in required:
        check((root / relative).is_file(), "CLK_REPO_REQUIRED_FILE", relative, errors)
    if errors:
        return errors

    version = utf8_lf_text(root / "VERSION", errors).strip()
    check(version == VERSION, "CLK_REPO_VERSION", repr(version), errors)

    actual_skills = tuple(
        sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
    )
    check(
        actual_skills == tuple(sorted(EXPECTED_SKILLS)),
        "CLK_REPO_SKILL_SET",
        repr(actual_skills),
        errors,
    )
    for name in EXPECTED_SKILLS:
        path = SKILLS_ROOT / name / "SKILL.md"
        check(path.is_file(), "CLK_REPO_SKILL_FILE", name, errors)
        if path.is_file():
            text = utf8_lf_text(path, errors)
            check(frontmatter_name(text) == name, "CLK_REPO_SKILL_NAME", name, errors)
            check(
                "description: Use when " in text,
                "CLK_REPO_SKILL_DESCRIPTION",
                name,
                errors,
            )

    main = utf8_lf_text(SKILLS_ROOT / "chain-loop-skill" / "SKILL.md", errors)
    for name in EXPECTED_SKILLS[1:]:
        check(main.count(f"`${name}`") == 1, "CLK_REPO_ROUTE", name, errors)
    check("`$small-loop-skill`" in main, "CLK_REPO_SLK_ROUTE", "main", errors)
    check("`$slk-" not in main, "CLK_REPO_SLK_CHILD_ROUTE", "main", errors)

    for relative in ("README.md", "README.zh-CN.md", "MIGRATION.md", "CHANGELOG.md"):
        utf8_lf_text(root / relative, errors)

    try:
        manifest = json.loads(utf8_lf_text(root / "MANIFEST.json", errors))
    except json.JSONDecodeError as exc:
        errors.append(f"CLK_REPO_MANIFEST_JSON: {exc}")
        return errors

    check(
        manifest.get("name") == COLLECTION_NAME,
        "CLK_REPO_MANIFEST_NAME",
        repr(manifest.get("name")),
        errors,
    )
    check(
        manifest.get("version") == VERSION,
        "CLK_REPO_MANIFEST_VERSION",
        repr(manifest.get("version")),
        errors,
    )
    check(
        manifest.get("skill_count") == len(EXPECTED_SKILLS),
        "CLK_REPO_MANIFEST_SKILLS",
        repr(manifest.get("skill_count")),
        errors,
    )
    check(
        manifest.get("excludes") == sorted(EXCLUDED_FILES),
        "CLK_REPO_MANIFEST_EXCLUDES",
        repr(manifest.get("excludes")),
        errors,
    )
    listed = {
        item.get("path"): item.get("sha256")
        for item in manifest.get("files", [])
        if isinstance(item, dict)
    }
    actual = {path.as_posix() for path in release_files(root)}
    check(
        set(listed) == actual,
        "CLK_REPO_MANIFEST_SET",
        f"missing={sorted(actual-set(listed))}; extra={sorted(set(listed)-actual)}",
        errors,
    )
    for relative, expected in listed.items():
        path = root / relative
        if path.is_file():
            check(sha256(path) == expected, "CLK_REPO_MANIFEST_HASH", relative, errors)
    return errors


def main(argv: Iterable[str]) -> int:
    args = list(argv)
    if args == ["--write-manifest"]:
        write_manifest(ROOT)
        print("WROTE: MANIFEST.json")
        return 0
    if args:
        print(
            "FAIL CLK_REPO_USAGE: optional argument is --write-manifest",
            file=sys.stderr,
        )
        return 2
    errors = validate(ROOT)
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("PASS: CLK 3.0 skill collection structure, identity, and Manifest are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
