from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MAIN_SKILL = "chain-loop-skill"
EXPECTED_CHILDREN = (
    "clk-plan-run",
    "clk-design-fusion-contracts",
    "clk-plan-parallel-isolation",
    "clk-grill-supervisor",
    "clk-launch-chains",
    "clk-complete-chain",
    "clk-start-fusion",
    "clk-close-run",
)
EXPECTED_SKILLS = (MAIN_SKILL, *EXPECTED_CHILDREN)

ADVISORY_REVIEW_TERMS = (
    "必须",
    "不得",
    "禁止",
    "只能",
    "一律",
    "MUST",
    "NEVER",
    "FORBIDDEN",
    "fail-closed",
    "fail closed",
)


def skill_path(name: str) -> Path:
    return SKILLS / name / "SKILL.md"


def read_skill(name: str) -> str:
    path = skill_path(name)
    assert path.is_file(), f"missing Skill: {path.relative_to(ROOT).as_posix()}"
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n"), "SKILL.md does not start with YAML frontmatter"
    try:
        raw, _body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise AssertionError("SKILL.md frontmatter is not closed") from exc
    values: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.fullmatch(r"([a-zA-Z0-9_-]+):\s*[\"']?(.*?)[\"']?", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def guidance_warnings(text: str) -> list[str]:
    warnings = [term for term in ADVISORY_REVIEW_TERMS if term in text]
    if re.search(r"(?:^|\n)\s*STOP\b", text):
        warnings.append("direct STOP instruction")
    return warnings


def size_diagnostics(name: str, text: str) -> list[str]:
    body = text.split("\n---\n", 1)[-1]
    lines = len(body.splitlines())
    chars = len(body)
    diagnostics: list[str] = []
    if lines > 90:
        diagnostics.append(f"{name}: review length {lines} lines")
    if chars > 6000:
        diagnostics.append(f"{name}: review size {chars} characters")
    return diagnostics


def assert_skill_shape(name: str) -> None:
    text = read_skill(name)
    values = parse_frontmatter(text)
    assert values.get("name") == name
    description = values.get("description", "")
    assert description.startswith("Use when ")
    assert guidance_warnings(text) == []
