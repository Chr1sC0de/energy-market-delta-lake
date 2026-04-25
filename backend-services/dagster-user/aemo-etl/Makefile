PHONY: integration-test

integration-test:
	uv run pytest --testmon -n=4 tests/integration

unit-test:
	uv run pytest --cov-fail-under=100 --cov=aemo_etl --cov-report=term-missing --cov-report=html -n=4 tests/unit

duplicate-check:
	uv run pylint --disable=all --enable=R0801 .

run-prek:
	prek run -a --fail-fast
