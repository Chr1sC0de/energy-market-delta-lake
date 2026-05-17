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
    assert "--version" in result.output


def test_console_script_entrypoint_is_declared() -> None:
    with (SUBPROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    scripts = pyproject["project"]["scripts"]

    assert scripts["gas-market-kb"] == "gas_market_knowledge_base.cli:main"
