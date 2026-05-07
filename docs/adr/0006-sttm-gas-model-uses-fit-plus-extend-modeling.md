# STTM gas_model Coverage Uses Fit-Plus-Extend Modeling

Manifest-backed STTM coverage extends the shared `gas_model` layer with
**Fit-plus-extend modeling**. Existing `gas_model` facts and dimensions receive
STTM rows where a report's grain and meaning match the current asset. New
`gas_model` facts are added where a report has a real STTM grain that does not
fit current assets without hiding domain fields or changing the asset meaning.

The policy applies to the STTM public reports backed by the checked-in v19.1
manifest: `INT651` through `INT684` and `INT687` through `INT691`. The detailed
report-to-destination mapping remains in
[architecture-exploration.md](../repository/architecture-exploration.md#issue-116-sttm-report-to-gas-model-mapping);
this ADR records the accepted modeling decision for follow-on implementation.

`INT685` and `INT685B` remain explicit **Source-spec gaps**. They are live
NEMWeb STTM root CSV reports, and discovery may land them, but they stay outside
source-table bronze, source silver, and `gas_model` coverage until AEMO document
discovery provides usable source definitions for their fields, grain, and
meaning.

## Considered options

- Force every manifest-backed STTM report into current `gas_model` facts:
  maximizes reuse, but overloads fact meanings, hides distinct STTM grains, and
  risks dropping source-specific fields that are meaningful to downstream gas
  reporting.
- Create a disconnected STTM-only `gas_model` area: preserves every source
  shape, but duplicates shared gas-market concepts, weakens cross-market
  reporting, and makes STTM coverage feel separate from GBB and VICGAS coverage.
- Use **Fit-plus-extend modeling**: keeps shared dimensions and facts as the
  first destination when the grain matches, while allowing new shared facts for
  STTM grains that are not represented today.

## Consequences

Follow-on STTM implementation issues should first check whether a report can
enrich an existing `gas_model` asset at the accepted grain. If it can, the
implementation should add STTM rows to that asset with source lineage. If it
cannot, the implementation should add a new `gas_model` fact with an explicit
grain instead of forcing the report into a near-fit asset.

The `gas_model` layer remains the shared gas-market mart, not a set of
source-specific silos. STTM-specific fact names are acceptable when the grain is
STTM-specific, but those facts still belong to `silver.gas_model` and should use
the same source-lineage conventions as existing facts.

Report coverage remains manifest-backed. `INT685` and `INT685B` should stay
visible as **Source-spec gaps** in docs and issue shaping until a separate AEMO
document-discovery path produces source definitions that can be reviewed.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `docs/repository/architecture-exploration.md`
  - `docs/adr/0003-bounded-current-state-bronze-source-tables.md`
  - `backend-services/dagster-user/aemo-etl/README.md`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/README.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/source_tables.json`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `prek run -a`
  - `verify STTM fit-plus-extend policy, source-spec gaps, and links match maintained docs`
