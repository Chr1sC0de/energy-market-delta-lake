from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".agents" / "skills" / "repo-knowledge-base" / "SKILL.md"
AGENTS_README_PATH = REPO_ROOT / "docs" / "agents" / "README.md"
ISSUE_TRACKER_PATH = REPO_ROOT / "docs" / "agents" / "issue-tracker.md"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"


class RepoKnowledgeBaseSkillContractTests(unittest.TestCase):
    def test_skill_exists_with_trigger_frontmatter(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: repo-knowledge-base", text)
        self.assertIn("Use when asked repo knowledge", text)
        self.assertIn("gas-market corpus questions", text)
        self.assertIn("generated bronze/silver/gold artifacts", text)
        self.assertIn("generated chunks", text)
        self.assertIn("Market context drafting/review", text)

    def test_skill_prioritizes_generated_artifacts_for_market_questions(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("generated/gold", text)
        self.assertIn("generated/silver/index/chunks.jsonl", text)
        self.assertIn("generated/silver/chunks", text)
        self.assertIn("generated/silver/documents", text)
        self.assertIn("generated/bronze/source_manifest.jsonl", text)
        self.assertIn("Search the generated corpus with `rg`", text)
        self.assertIn("open the cited chunk files", text)

    def test_skill_requires_chunk_citations_for_factual_synthesis(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Every factual gas-market claim must cite generated evidence", text)
        self.assertIn("`chunk_id`", text)
        self.assertIn("chunk file path", text)
        self.assertIn("`content_sha256`", text)
        self.assertIn("source document Markdown path", text)
        self.assertIn("Reject or flag uncited factual synthesis", text)
        self.assertIn("not supported by the generated artifacts", text)
        self.assertIn("Mark inference separately from direct source evidence", text)

    def test_skill_distinguishes_generated_corpus_from_maintained_docs(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Maintained repo docs", text)
        self.assertIn("**Documentation sync**", text)
        self.assertIn("Generated corpus artifacts live under", text)
        self.assertIn("not maintained router\n  documentation", text)
        self.assertIn("must not get sync metadata", text)
        self.assertIn("Do not copy bronze, silver, or gold corpus content", text)

    def test_skill_and_docs_note_full_access_boundary_for_agents_paths(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        issue_tracker = ISSUE_TRACKER_PATH.read_text(encoding="utf-8")

        for text in (skill, issue_tracker):
            normalized = " ".join(text.split())
            self.assertIn(".agents/", text)
            self.assertIn("**Full-access implementation pass**", normalized)
        self.assertIn("operator-approved **Full-access implementation pass**", issue_tracker)
        self.assertIn("`.agents/skills/`", issue_tracker)
        self.assertIn("$repo-knowledge-base", issue_tracker)

    def test_agent_docs_route_to_skill_and_track_sync_source(self) -> None:
        text = AGENTS_README_PATH.read_text(encoding="utf-8")

        self.assertIn("$repo-knowledge-base", text)
        self.assertIn("../../.agents/skills/repo-knowledge-base/SKILL.md", text)
        self.assertIn("generated chunk citation", text)
        self.assertIn("`.agents/skills/repo-knowledge-base/SKILL.md`", text)

    def test_gitignore_allows_repo_knowledge_base_skill_tracking(self) -> None:
        text = GITIGNORE_PATH.read_text(encoding="utf-8")

        self.assertIn("!.agents/skills/repo-knowledge-base", text)
        self.assertIn("!.agents/skills/repo-knowledge-base/SKILL.md", text)


if __name__ == "__main__":
    unittest.main()
