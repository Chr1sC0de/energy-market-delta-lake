.PHONY: unit-test fast-test run-prek

unit-test:
	uv run pytest tests/unit -q

fast-test: unit-test

run-prek:
	prek run -a --fail-fast
