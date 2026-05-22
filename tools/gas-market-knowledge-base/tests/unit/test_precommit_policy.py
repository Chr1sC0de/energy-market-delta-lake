import re
from pathlib import Path

SUBPROJECT_ROOT = Path(__file__).resolve().parents[2]


def _large_file_exclude_regex() -> re.Pattern[str]:
    config_text = (SUBPROJECT_ROOT / ".pre-commit-config.yaml").read_text(
        encoding="utf-8"
    )
    hook_match = re.search(
        r"- id: check-added-large-files\n"
        r"\s+args: \[--maxkb=500\]\n"
        r"\s+exclude: (?P<exclude>[^\n]+)\n",
        config_text,
    )

    assert hook_match is not None
    return re.compile(hook_match.group("exclude"))


def test_large_file_hook_allows_generated_silver_document_markdown() -> None:
    silver_document_path = (
        "generated/silver/documents/sttm/sttm-procedures-2025/"
        "sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md"
    )
    repo_relative_silver_document_path = (
        f"tools/gas-market-knowledge-base/{silver_document_path}"
    )
    exclude_regex = _large_file_exclude_regex()

    assert exclude_regex.fullmatch(silver_document_path)
    assert exclude_regex.fullmatch(repo_relative_silver_document_path)


def test_large_file_hook_still_checks_unrelated_large_files() -> None:
    exclude_regex = _large_file_exclude_regex()

    assert not exclude_regex.fullmatch(
        "generated/silver/chunks/sttm/sttm-procedures-2025/chunk.md"
    )
    assert not exclude_regex.fullmatch(
        "tools/gas-market-knowledge-base/generated/silver/chunks/sttm/"
        "sttm-procedures-2025/chunk.md"
    )
    assert not exclude_regex.fullmatch("generated/gold/sttm-procedures.md")
    assert not exclude_regex.fullmatch(
        "generated/silver/documents/sttm/sttm-procedures-2025/source.pdf"
    )
    assert not exclude_regex.fullmatch(
        "generated/silver/documents/sttm/sttm-procedures-2025/source.bin"
    )
