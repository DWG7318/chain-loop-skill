# CLK Loop Engineering Identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define CLK as the composite Loop Engineering form built from complete SLK Loops with the smallest necessary replacements.

**Architecture:** Preserve the nine-Skill CLK collection. Replace the main identity sentences plus one launch sentence and one Fusion preparation sentence, add semantic assertions to the existing test module, and propagate patch version 3.0.2 through existing carriers.

**Tech Stack:** Markdown Skills, Python `pytest`, repository validator, Skill quick validator.

---

### Task 1: Lock the composite Loop identity

**Files:**
- Modify: `tests/test_skill_collection_300.py`
- Modify: `skills/chain-loop-skill/SKILL.md`
- Modify: `skills/clk-launch-chains/SKILL.md`
- Modify: `skills/clk-start-fusion/SKILL.md`

- [ ] **Step 1: Add failing semantic assertions to the existing CLK clarification test**

```python
assert "Loop Engineering 的复合形态" in main
assert "每条前置 Chain 都是一个完整的 SLK Loop" in main
assert "Fusion Chain 也是一个完整的 SLK Loop" in main
assert "消息只传输 Loop 工作和结果" in main
assert "每条Chain作为一个完整SLK Loop" in launch
assert "Fusion Chain 本身是一个完整的 SLK Loop" in fusion
```

- [ ] **Step 2: Run the focused test and confirm RED**

Run: `python -m pytest tests/test_skill_collection_300.py::test_clk_roles_end_their_turn_instead_of_waiting_on_or_watching_chains -q`

Expected: FAIL because the composite Loop identity markers are absent.

- [ ] **Step 3: Make only sentence replacements in the three Skills**

Use these meanings without adding sections or Skill lines:

```text
CLK 是建立在 SLK Loop 之上的 Loop Engineering 复合形态；一个 CLK 对应一个 Run。
每条前置 Chain 都是一个完整的 SLK Loop，并发形成冻结成果。
Fusion Chain 也是一个完整的 SLK Loop，可含一个或多个线性 GO，并由最终 D2 闭合 CLK Run。
消息只传输 Loop 工作和结果；完成当前 Loop 节点后结束活动，接收回执不代表节点完成。
```

- [ ] **Step 4: Run focused test and confirm GREEN**

Run: `python -m pytest tests/test_skill_collection_300.py::test_clk_roles_end_their_turn_instead_of_waiting_on_or_watching_chains -q`

Expected: `1 passed`.

- [ ] **Step 5: Confirm Skill line counts did not grow**

Run: `python -m pytest tests/test_skill_collection_300.py::test_clk_wait_clarification_does_not_add_skill_lines -q`

Expected: `1 passed` with the existing nine-file line-count map unchanged.

### Task 2: Propagate patch identity and validate

**Files:**
- Modify: `VERSION`
- Modify: `MANIFEST.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `CHANGELOG.md`
- Modify: `VALIDATION-REPORT.md`
- Modify: `scripts/validate_repository.py`
- Modify: `tests/test_repository_300.py`
- Modify: `tests/test_skill_collection_300.py`

- [ ] **Step 1: Change only current-version carriers from 3.0.1 to 3.0.2**

Keep all historical `3.0.1` changelog content. Add one `3.0.2` changelog entry describing the composite Loop identity. Recompute only affected Manifest SHA-256 entries using the repository's existing manifest convention.

- [ ] **Step 2: Run the full repository gates**

Run:

```powershell
python scripts/validate_repository.py
python scripts/quick_validate.py skills
python -m pytest -q
python -O -m pytest -q
git diff --check
```

Expected: repository PASS, nine Skill directories PASS, all tests PASS in normal and optimized Python, and no diff errors.

- [ ] **Step 3: Commit the implementation candidate**

```powershell
git add CHANGELOG.md MANIFEST.json README.md README.zh-CN.md VALIDATION-REPORT.md VERSION scripts/validate_repository.py skills tests
git commit -m "fix: define CLK as composite Loop Engineering"
```
