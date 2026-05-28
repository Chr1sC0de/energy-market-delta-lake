.PHONY: unit-test docling-adapter-test fast-test run-prek \
	aemo-publications-unit-test aemo-publications-run-prek

unit-test:
	uv run pytest tests/unit -q

aemo-publications-unit-test:
	uv run pytest tests/unit/test_aemo_publications.py -q

# Real Docling adapter smoke; excluded from Unit test and Commit check lanes.
docling-adapter-test:
	uv run pytest tests/docling -q

fast-test: unit-test

run-prek:
	prek run -a --fail-fast

aemo-publications-run-prek: run-prek
