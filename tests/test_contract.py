from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
IGNORED_REPOSITORY_PARTS = {
    ".git",
    ".codex",
    ".worktrees",
    ".pytest_cache",
    "__pycache__",
}
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
PROMPT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
DETECTION_REFERENCE = (ROOT / "references" / "checker-detection-catalog.md").read_text(
    encoding="utf-8"
)
CONTROL_REFERENCE = (ROOT / "references" / "mslk-control-operations.md").read_text(
    encoding="utf-8"
)
CONTROL_CONTRACT = json.loads(
    (ROOT / "contracts" / "mslk-control-kernel.json").read_text(encoding="utf-8")
)
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
ALL_TEXT = "\n".join((SKILL, README, PROMPT, DETECTION_REFERENCE))
NORMALIZED_SKILL = " ".join(SKILL.split())
NORMALIZED_DETECTION = " ".join((SKILL + "\n" + DETECTION_REFERENCE).split())


def governed_markdown_paths():
    return (
        path
        for path in ROOT.rglob("*.md")
        if not any(
            part in IGNORED_REPOSITORY_PARTS
            for part in path.relative_to(ROOT).parts
        )
    )


class MultiSmallLoopContractTest(unittest.TestCase):
    def test_required_operational_links_are_explicit(self):
        required = (
            "(scripts/run_mslk_readiness_eval.py)",
            "(evals/mslk-readiness-questions.json)",
            "(contracts/mslk-control-kernel.json)",
            "(references/mslk-control-operations.md)",
            "(references/checker-detection-catalog.md)",
        )
        for link in required:
            with self.subTest(link=link):
                self.assertIn(link, SKILL)

    def test_markdown_reference_graph_is_closed_and_bounded(self):
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        queue = [ROOT / "SKILL.md"]
        visited = set()
        while queue:
            source = queue.pop()
            if source in visited:
                continue
            visited.add(source)
            text = source.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(text):
                target_text = raw_target.split("#", 1)[0]
                if not target_text or "://" in target_text:
                    continue
                target = (source.parent / target_text).resolve()
                self.assertTrue(target.is_relative_to(ROOT.resolve()), raw_target)
                self.assertTrue(target.is_file(), raw_target)
                if target.suffix.lower() == ".md":
                    queue.append(target)

        for reference in CONTROL_CONTRACT["references"]:
            target = (ROOT / reference).resolve()
            self.assertTrue(target.is_relative_to(ROOT.resolve()), reference)
            self.assertTrue(target.is_file(), reference)
            queue.append(target)

        reference_files = set((ROOT / "references").glob("*.md"))
        self.assertTrue(reference_files.issubset(visited | set(queue)))
        for path in governed_markdown_paths():
            self.assertLessEqual(
                len(path.read_text(encoding="utf-8").splitlines()), 1000, path
            )
        self.assertLess(len(SKILL.splitlines()), 900)

    def test_release_identity_is_clk_v2_6_0_with_legacy_assets_preserved(self):
        self.assertEqual(VERSION, "2.6.0")
        self.assertIn("Current version: **2.6.0**", README)
        self.assertIn("GitHub repository ID: `1298120736`", SKILL)
        self.assertIn("Multi Small Loop Skill", SKILL)
        self.assertNotIn("all nine rules", README.lower())

    def test_readiness_precedes_simulation_and_manual_frozen_start(self):
        self.assertIn("## Mandatory Readiness Eval", SKILL)
        self.assertIn("MSLK_READINESS_EVAL_PASS", SKILL)
        self.assertIn("exactly `25/25`", SKILL)
        self.assertIn("complete frozen roster", SKILL)
        self.assertLess(
            SKILL.index("## Mandatory Readiness Eval"),
            SKILL.index("## Mandatory Simulation Gate"),
        )
        self.assertEqual(CONTROL_CONTRACT["initial_start"], "MSLK START")
        self.assertTrue(CONTROL_CONTRACT["roster_frozen_after_start"])
        self.assertNotIn("SCHEDULED_START", SKILL)
        self.assertNotIn("create a not-yet-created pair", SKILL)

    def test_continuation_index_is_bounded_current_state(self):
        self.assertIn("bounded mutable current-state pointer", NORMALIZED_SKILL)
        self.assertIn("below 200 physical lines", NORMALIZED_SKILL)
        self.assertIn(
            "Historical detail remains in linked semantic shards", NORMALIZED_SKILL
        )

    def test_main_skill_context_is_below_target(self):
        self.assertLess(len(SKILL.splitlines()), 900)

    def test_mode_is_strictly_exclusive(self):
        self.assertIn("invoke MSLK exactly once", SKILL)
        self.assertIn("do not borrow SLK's combined Supervisor/Checker", SKILL)
        self.assertIn("Shared rules never transfer role ownership", SKILL)
        self.assertIn("current run never converts itself into SLK", SKILL)
        self.assertIn("Never load, borrow, combine, or switch to SLK", PROMPT)

    def test_topology_and_role_ownership(self):
        self.assertIn(
            "one distinct Supervisor plus multiple persistent Checker/Worker pairs",
            SKILL,
        )
        self.assertIn(
            "project decomposition, cross-Worker contracts, Supervisor board, and final audit | Supervisor",
            SKILL,
        )
        self.assertIn(
            "initial solution, GO/CELL plan, and evidence-driven GO revision | Its paired Checker",
            SKILL,
        )
        self.assertIn(
            "CELL assignment, validation, repair, routing, progress display, and per-Worker queue | Its paired Checker",
            SKILL,
        )
        self.assertNotIn("Produce or approve each Worker", SKILL)
        self.assertNotIn("fixed retry policy", SKILL)
        self.assertIn("Send formal tasks directly to its paired Worker", SKILL)
        self.assertIn("never subagents or a combined role", PROMPT)

    def test_optional_goal_gate_preserves_checker_planning(self):
        required = (
            "## Optional Goal Gate",
            "The Owner may define one optional Goal",
            "Checker completion is provisional",
            "The Supervisor must independently validate the Goal",
            "GOAL_SATISFIED",
            "GOAL_GAP",
            "must not declare project completion",
            "Each affected Checker designs its own PLAN/GO/CELL continuation",
            "The Supervisor must not author those detailed Checker plans",
            "If no Goal is configured",
            "An untested Goal or `GOAL_GAP` remains unfinished Supervisor work",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)

    def test_continuation_condition_gate_stops_checker_dispatch(self):
        required = (
            "## Continuation Condition Gate",
            "The Checker must stop dispatching formal tasks",
            "CONDITION_BLOCKED",
            "report the condition to the Supervisor",
            "The Supervisor decides whether Owner assistance is required",
            "OWNER_ASSISTANCE_REQUIRED",
            "OWNER_ASSISTANCE_RECEIVED",
            "SUPERVISOR_RESOLVED",
            "RESUME_AUTHORIZED",
            "wake the same Checker",
            "The Checker must revalidate every blocked condition before dispatching",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)

    def test_control_commands_pause_and_resume_existing_pairs_safely(self):
        normalized_control = " ".join((SKILL + "\n" + CONTROL_REFERENCE).split())
        required = (
            "## MSLK Control Commands",
            "`MSLK START` is manual only",
            "MSLK PAUSE ALL AFTER <accepted-cell-count>",
            "MSLK PAUSE PAIR <pair-id> AFTER <accepted-cell-count>",
            "MSLK RESUME PAIR <pair-id> AT <RFC3339-time>",
            "absolute project-wide accepted CELL count",
            "`MSLK_CONTROL_RECEIPT`",
            "must not interrupt an active CELL",
            "wake the same Checker",
            "A paused pair is not complete",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, normalized_control)
        self.assertNotIn("SCHEDULED_START", SKILL)

    def test_dispatch_is_final_action_and_paired_checker_goes_offline(self):
        required = (
            "## Dispatch-Then-Offline Boundary",
            "The formal Worker assignment is the Checker's final action",
            "OFFLINE_WAITING_WORKER_SIGNAL",
            "must immediately end its turn and go offline",
            "must not poll, inspect, run status, perform oversight, or do more pair work",
            "WORKER_COMPLETION_RECEIPT",
            "WORKER_BLOCKER_RECEIPT",
            "WORKER_EXECUTION_FAILURE",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)

        boundary = CONTROL_CONTRACT["dispatch_boundary"]
        self.assertEqual(boundary["controller"], "paired Checker")
        self.assertTrue(boundary["assignment_is_final_action"])
        self.assertEqual(boundary["post_dispatch_state"], "OFFLINE_WAITING_WORKER_SIGNAL")
        self.assertEqual(
            boundary["wake_signals"],
            [
                "WORKER_COMPLETION_RECEIPT",
                "WORKER_BLOCKER_RECEIPT",
                "WORKER_EXECUTION_FAILURE",
            ],
        )
        self.assertFalse(boundary["checker_periodic_worker_inspection"])

    def test_only_supervisor_may_contact_owner(self):
        required = (
            "## Owner Assistance Authority",
            "A Worker must never ask the Owner",
            "A Checker must never ask the Owner",
            "Only the Supervisor may contact the Owner",
            "minimize Owner assistance",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)

        authority = CONTROL_CONTRACT["owner_assistance"]
        self.assertFalse(authority["worker_may_contact_owner"])
        self.assertFalse(authority["checker_may_contact_owner"])
        self.assertEqual(authority["sole_contact_authority"], "Supervisor")

    def test_supervisor_patrol_is_last_progress_guarantee(self):
        required = (
            "## Supervisor Safeguard Patrol",
            "last guarantee that work continues",
            "highest on-site decision authority",
            "authorization repair",
            "versioned plan revision",
            "work-method improvement",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)

        patrol = CONTROL_CONTRACT["supervisor_patrol"]
        self.assertEqual(patrol["actor"], "Supervisor")
        self.assertTrue(patrol["highest_on_site_decision_authority"])
        self.assertFalse(patrol["wake_healthy_offline_checker"])
        self.assertEqual(
            patrol["powers"],
            ["authorization_repair", "versioned_plan_revision", "work_method_improvement"],
        )

    def test_worker_execution_is_preauthorized_before_dispatch(self):
        required = (
            "## Pre-Authorized Worker Execution Gate",
            "canonical workspace path",
            "must exactly match the Worker's bound conversation workspace",
            "pre-authorize every routine operation inside the CELL allowlist",
            "must never be delegated to the Owner",
            "WORKER_EXECUTION_FAILURE",
            "Owner-only decision",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)

        gate = CONTROL_CONTRACT["worker_execution_gate"]
        self.assertEqual(gate["dispatcher"], "paired Checker")
        self.assertEqual(gate["permission_provisioner"], "Supervisor")
        self.assertTrue(gate["workspace_binding_required"])
        self.assertTrue(gate["allowlist_preauthorized"])
        self.assertTrue(gate["owner_routine_approval_forbidden"])
        self.assertEqual(
            gate["unexpected_routine_approval_signal"],
            "WORKER_EXECUTION_FAILURE",
        )

    def test_quick_inspection_uses_the_single_control_reference(self):
        self.assertIn("## Quick Inspection", CONTROL_REFERENCE)
        self.assertIn("## Wake Rule", CONTROL_REFERENCE)
        self.assertIn("## Overseer Record", CONTROL_REFERENCE)
        self.assertIn(
            "references/mslk-control-operations.md", CONTROL_CONTRACT["references"]
        )
        self.assertNotIn("overseer-inspection-and-wake.md", SKILL)

    def test_checker_detection_system_and_supervisor_capability_supply(self):
        required = (
            "## Checker Detection System",
            "Every Checker must maintain one evolving detection system",
            "The Supervisor must provision every Checker",
            "DETECTION_CAPABILITY_MANIFEST",
            "mature detection skills",
            "`superpowers:verification-before-completion`",
            "`superpowers:systematic-debugging`",
            "`superpowers:test-driven-development`",
            "`security-best-practices`",
            "`playwright`",
            "skill source, version, and compatibility",
            "Any skill that requires subagents is incompatible",
            "CodeGraph is mandatory for code or repository work",
            "layered detection stack",
            "Semgrep or CodeQL",
            "Gitleaks",
            "OSV-Scanner or Trivy",
            "Playwright",
            "coverage and mutation testing",
            "API or schema contract",
            "tool version, configuration, and omission rationale",
            "split or serialize the detection commands",
            "not acceptance quality",
            "structural and dependency baseline",
            "acceptance matrix",
            "false-positive",
            "REGRESSION_EVIDENCE",
            "CONDITION_BLOCKED",
            "must not accept a CELL from Worker self-report alone",
            "update the next CELL, GO revision, or supplementary GO",
            "Checker-specific tool access",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_DETECTION)

    def test_go_detection_profile_is_planned_and_executed_for_every_cell(self):
        required = (
            "Every GO plan must declare one `GO_DETECTION_PROFILE`",
            "skills and tools are assigned to the GO, never ad hoc to a CELL",
            "The owning Checker writes the profile",
            "The Supervisor provisions and approves it",
            "The paired Checker is the sole routine user of the assigned detection bundle",
            "Every CELL in that GO must execute every required skill and tool",
            "CELL_DETECTION_RECEIPT",
            "No required GO-level capability may be skipped",
            "Worker-run checks do not satisfy this Checker obligation",
            "If a capability is irrelevant to any CELL, redesign or split the GO",
            "Changing the bundle requires a versioned GO plan revision",
            "before the next CELL is dispatched",
            "arguments and affected paths may narrow per CELL, but capability membership may not",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)
        self.assertNotIn("Not every optional layer runs for every CELL", SKILL)

    def test_markdown_context_boundary_is_hard_and_semantic(self):
        required = (
            "## Markdown Context Boundary",
            "Every Markdown file governed by the loop has a hard maximum of 1000 physical lines",
            "This is a Codex context-readability limit, not a device-capacity limit",
            "A stronger computer, model, or context window does not waive it",
            "WORK_CONTINUATION_INDEX",
            "MD_LINE_BUDGET_PASS",
            "split at a semantic work-continuation boundary",
            "must not hard-cut a requirement, table, code block, acceptance record, or evidence chain",
            "before the next append would exceed 1000 lines",
            "Every CELL acceptance checks all created or materially expanded Markdown files",
            "After context compaction or a shard transition",
            "read-only source or third-party Markdown",
            "markdown-line-budget",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, NORMALIZED_SKILL)
        self.assertNotIn("999 lines", SKILL)
        for path in governed_markdown_paths():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertLessEqual(len(path.read_text(encoding="utf-8").splitlines()), 1000)

    def test_shared_rules_remain_inside_mslk(self):
        required = (
            "Never use a subagent",
            "SIMULATION_PASS",
            "Archive it immediately",
            "GO_REVISION_SIMULATION_PASS",
            "must not send a repair task back to the Worker",
            "compatibility evaluation uses `gpt-5.6-terra+xhigh`",
            "GPT 5.5 and lower are rejected",
            "GO scope follows project need and must not be reduced for device capacity",
            "CELL size must be kept modest enough for the current computer",
            "正在完成 GO-03：35/231",
            "全部完成：231/231",
            "not a per-Worker subtotal",
            "Supervisor remains the sole writer of the Supervisor board",
        )
        for rule in required:
            with self.subTest(rule=rule):
                self.assertIn(rule, ALL_TEXT)

        self.assertNotIn("Formal rework:", ALL_TEXT)
        self.assertNotIn("planner", ALL_TEXT.lower())


if __name__ == "__main__":
    unittest.main()
