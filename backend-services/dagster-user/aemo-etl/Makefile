.PHONY: unit-test component-test fast-test integration-test integration-test-testmon duplicate-check run-prek

integration-test:
	LOCAL_INTEGRATION_TESTS=1 uv run pytest -n=4 tests/integration

integration-test-testmon:
	LOCAL_INTEGRATION_TESTS=1 uv run pytest --testmon -n=4 tests/integration

unit-test:
	uv run pytest -n=4 tests/unit

component-test:
	uv run pytest -n=4 tests/component

fast-test:
	uv run pytest --cov-fail-under=100 --cov=aemo_etl --cov-report=term-missing --cov-report=html -n=4 tests/unit tests/component

duplicate-check:
	uv run pylint --persistent=n --disable=all --enable=R0801 --ignore-paths='^src/aemo_etl/defs/raw/.*' src

run-prek:
	prek run -a --fail-fast
