import subprocess
import sys
import tomllib
from pathlib import Path

from click.testing import CliRunner

from gas_market_knowledge_base import __version__
from gas_market_knowledge_base.cli import main

SUBPROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_cli_help_renders() -> None:
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Work with Gas market knowledge base artifacts." in result.output
    assert "audit-archive-prefix" in result.output
    assert "build-index" in result.output
    assert "extract-silver" in result.output
    assert "fetch-pdfs" in result.output
    assert "sync-manifest" in result.output
    assert "validate" in result.output
    assert "--version" in result.output


def test_generated_path_help_mentions_corpus_root_env() -> None:
    result = CliRunner().invoke(main, ["validate", "--help"])
    compact_output = result.output.replace("\n", "").replace(" ", "")

    assert result.exit_code == 0
    assert "ENERGY_MARKET_CORPUS_ROOT" in result.output
    assert "gas-market/silver/index/chunks.jsonl" in compact_output
    assert "gas-market/gold" in compact_output


def test_runtime_imports_do_not_require_s3_type_stubs() -> None:
    script = """
import builtins

real_import = builtins.__import__

def guarded_import(name, *args, **kwargs):
    if name == "types_boto3_s3" or name.startswith("types_boto3_s3."):
        raise ModuleNotFoundError(name)
    return real_import(name, *args, **kwargs)

builtins.__import__ = guarded_import

import gas_market_knowledge_base.pdf_cache
import gas_market_knowledge_base.cli
"""

    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        cwd=SUBPROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_console_script_entrypoint_is_declared() -> None:
    with (SUBPROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    scripts = pyproject["project"]["scripts"]

    assert (
        scripts["aemo-publications-corpus"]
        == "gas_market_knowledge_base.aemo_publications.cli:main"
    )
    assert scripts["gas-market-kb"] == "gas_market_knowledge_base.cli:main"
