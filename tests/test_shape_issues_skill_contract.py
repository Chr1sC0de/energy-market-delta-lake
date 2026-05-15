from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".agents" / "skills" / "shape-issues" / "SKILL.md"
GATE_CONTRACT_PATH = (
    REPO_ROOT / ".agents" / "skills" / "shape-issues" / "references" / "gate-contract.md"
)
CONTEXT_ASSESSORS_PATH = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "shape-issues"
    / "references"
    / "context-assessors.md"
)


class ShapeIssuesSkillContractTests(unittest.TestCase):
    def test_skill_documents_tracer_bullet_slice_classes(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("tracer-bullet", text)
        self.assertIn("thin vertical tracer-bullet slices", text)
        self.assertIn("every affected integration layer", text)
        self.assertIn("Do not create horizontal layer-only slices", text)
        self.assertIn("demonstrable\nend-to-end behavior", text)
        self.assertIn("`afk`", text)
        self.assertIn("`human-decision`", text)
        self.assertIn("`exploratory`", text)
        self.assertIn("Operator Quiz", text)
        self.assertIn("Issue context assessor", text)
        self.assertIn("context-assessors.md", text)

    def test_skill_keeps_human_decision_separate_from_exploratory_delivery(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Keep it out of the gate bundle by default", text)
        self.assertIn("instead of mapping it to **Exploratory delivery**", text)
        self.assertIn("must use `delivery-exploratory`", text)
        self.assertIn("include `## Review focus`", text)

    def test_skill_publish_contract_is_confirmed_needs_triage_only(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("requires the Operator to explicitly confirm", text)
        self.assertIn("refuses to run without `--confirm-publish`", text)
        self.assertIn("refuses fixture-gated non-dry-run publication", text)
        self.assertIn("`--allow-fixture-publish`", text)
        self.assertIn("creates only `needs-triage` issues", text)
        self.assertIn("never mutates existing issues", text)
        self.assertIn("source markers", text)

    def test_skill_documents_publisher_preflight_and_github_failure_diagnostics(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("non-dry-run GitHub CLI preflight", text)
        self.assertIn("before writing final body files", text)
        self.assertIn("failing phase, exit code, stderr summary", text)
        self.assertIn("stdout summary", text)

    def test_skill_documents_followup_command_guardrail(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Follow-up Command Guardrail", text)
        self.assertIn("`proceed`, `continue`, `do it`, or `implement the plan`", text)
        self.assertIn("mean `$shape-issues`\nexecution", text)
        self.assertIn("create or update the bundle, run the gate", text)
        self.assertIn("must not be interpreted as\ndirect implementation edits", text)
        self.assertIn("Direct implementation requires `$ralph-loop`", text)
        self.assertIn("specific GitHub Issue, such as `implement issue #123`", text)

    def test_gate_review_markdown_artifacts_are_documented(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        gate_contract = GATE_CONTRACT_PATH.read_text(encoding="utf-8")

        for text in (skill, gate_contract):
            self.assertIn("`issue-drafts.md`", text)
            self.assertIn("`issue-drafts/<issue-id>.md`", text)
        self.assertIn("pre-publication review Markdown", gate_contract)
        self.assertIn("blocker references by draft id", gate_contract)
        self.assertIn("full draft body", gate_contract)

    def test_fixture_publish_policy_is_documented_in_contracts(self) -> None:
        gate_contract = GATE_CONTRACT_PATH.read_text(encoding="utf-8")
        context_assessors = CONTEXT_ASSESSORS_PATH.read_text(encoding="utf-8")

        for text in (gate_contract, context_assessors):
            normalized = " ".join(text.split())
            self.assertIn("`--dry-run`", text)
            self.assertIn("`--allow-fixture-publish`", text)
            self.assertIn("publish-manifest.json", text)
            self.assertIn("final issue body", normalized)


if __name__ == "__main__":
    unittest.main()
