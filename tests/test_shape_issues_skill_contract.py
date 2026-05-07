from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".agents" / "skills" / "shape-issues" / "SKILL.md"


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
        self.assertIn("creates only `needs-triage` issues", text)
        self.assertIn("never mutates existing issues", text)
        self.assertIn("source markers", text)


if __name__ == "__main__":
    unittest.main()
