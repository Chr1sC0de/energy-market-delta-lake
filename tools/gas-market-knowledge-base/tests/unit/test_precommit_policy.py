import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SUBPROJECT_ROOT = Path(__file__).resolve().parents[2]
GITIGNORE_PATH = REPO_ROOT / ".gitignore"


def _hook_block(hook_id: str) -> str:
    config_text = (SUBPROJECT_ROOT / ".pre-commit-config.yaml").read_text(
        encoding="utf-8"
    )
    hook_match = re.search(
        rf"(?ms)^      - id: {re.escape(hook_id)}\n"
        r".*?(?=^      - id: |\Z)",
        config_text,
    )

    assert hook_match is not None
    return hook_match.group(0)


def _hook_files_regex(hook_id: str) -> re.Pattern[str]:
    files_match = re.search(
        r"^\s+files: (?P<files>[^\n]+)$",
        _hook_block(hook_id),
        re.MULTILINE,
    )

    assert files_match is not None
    return re.compile(files_match.group("files"))


def test_large_file_hook_has_no_generated_corpus_exception() -> None:
    hook_block = _hook_block("check-added-large-files")

    assert "args: [--maxkb=500]" in hook_block
    assert "exclude:" not in hook_block
    assert "generated/" not in hook_block


def test_generated_corpus_artifact_hook_blocks_bronze_silver_gold_paths() -> None:
    hook_block = _hook_block("forbid-generated-corpus-artifacts")
    files_regex = _hook_files_regex("forbid-generated-corpus-artifacts")

    assert "ENERGY_MARKET_CORPUS_ROOT" in hook_block
    assert files_regex.fullmatch("generated/bronze/source_manifest.jsonl")
    assert files_regex.fullmatch("generated/silver/index/chunks.jsonl")
    assert files_regex.fullmatch("generated/gold/glossary/README.md")
    assert files_regex.fullmatch(
        "tools/gas-market-knowledge-base/generated/silver/documents/"
        "sttm/sttm-procedures-2025/source.md"
    )
    assert not files_regex.fullmatch(".cache/pdfs/source.pdf")
    assert not files_regex.fullmatch("generated/silver-notes/example.md")
    assert not files_regex.fullmatch("README.md")


def test_gitignore_keeps_generated_corpus_tree_out_of_git() -> None:
    gitignore_lines = GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()

    assert "tools/gas-market-knowledge-base/generated/" in gitignore_lines
    assert not any(
        line.startswith("!tools/gas-market-knowledge-base/generated/")
        for line in gitignore_lines
    )
