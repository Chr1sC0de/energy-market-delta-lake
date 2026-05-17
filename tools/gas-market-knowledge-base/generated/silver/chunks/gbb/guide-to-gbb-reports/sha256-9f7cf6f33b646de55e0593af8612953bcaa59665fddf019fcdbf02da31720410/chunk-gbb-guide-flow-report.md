---
{
  "chunk_id": "chunk-gbb-guide-flow-report",
  "chunk_ordinal": 3,
  "chunk_text_sha256": "da19a4521b21ac8bf0ee2f09f80c8f57da19738603db0c0baeaeec5217e37fcc",
  "chunking_settings": {
    "chunker": "HybridChunker",
    "merge_peers": true,
    "omit_header_on_overflow": false,
    "repeat_table_header": true,
    "schema_version": 1,
    "tool": "docling-hybrid"
  },
  "chunking_settings_sha256": "a57e8b8018c83b551505462598681565b8effa3456c2824e782e833a2ef673eb",
  "chunking_tool": "docling-hybrid",
  "citations": {
    "doc_items": [
      {
        "extraction": "pdftotext-layout-seed",
        "label": "text",
        "source_text_line_end": 1090,
        "source_text_line_start": 1030
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md",
    "source_manifest_line_number": 4,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-gbb-procedures-for-renewable-gas/decision/guide-to-gas-bulletin-board-reports-v23.pdf?rev=583464be2e9642a0aed11973b1e09a80&sc_lang=en"
  },
  "content_sha256": "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
  "corpus": "gbb",
  "document_family": "gbb__guide-to-gas-bulletin-board-reports",
  "document_family_id": "gbb__guide-to-gas-bulletin-board-reports",
  "document_identity": "gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
  "document_title": "Guide to Gas Bulletin Board Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-flow-report.md",
  "heading_path": [
    "Guide to Gas Bulletin Board Reports",
    "Pipeline connection flow report"
  ],
  "path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-flow-report.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md"
}
---

Nomination and Forecasts report in JSON format can be filtered by:

           • Gas Date

           • FacilityId.

           • LocationId
           The report output contains the latest submission for that gas day. For requested past dates, this
           is the day ahead or on-the-day nominations and forecast submission. For future dates, the
           output is the latest nominations and forecast submission.

4.7.4. Example report
           Vist the AEMO developer portal for example for HTTPS GET request examples.

4.8. Pipeline Connection Flow
4.8.1. Description
 Transaction report    GASBB_PIPELINE_CONNECTION_FLOW / GASBB_PIPELINE_CONNECTION_FLOW_LAST_31
 name
 Purpose Provides a report for the Daily production and usage at each Connection Point.
 Production            GASBB_PIPELINE_CONNECTION_FLOW is updated daily.
 Frequency GASBB_PIPELINE_CONNECTION_FLOW_LAST_31 is typically updated within 30 minutes of
                       receiving new data
 Report Period GASBB_PIPELINE_CONNECTION_FLOW contains historical data from Sep 2018
                       GASBB_PIPELINE_CONNECTION_FLOW_LAST_31 contains data from the last 31 days.

4.8.2. Data report format

           The following fields are available in each row of the report.

 Field name                Description Data type Example
 GasDate Date of gas day. Timestamps are ignored.                datetime                2018-09-23
                           The gas day as defined in the pipeline contract or 00:00:00
                           market rules.
 FacilityId                A unique AEMO defined Facility identifier. Int 520345
 FacilityName Name of the facility. varchar (100) Berwyndale to
                                                                                                           Wallumbilla
                                                                                                           Pipeline
 ConnectionPointId A unique AEMO defined connection point Int 1200001
                           identifier.
 ConnectionPointName Names of the connection point. varchar (100) Longford

AEMO | 3 March 2025                                                                                              Page 19 of 45

Guide to Gas Bulletin Board Reports

 Field name Description Data type Example
 FlowDirection A conditional value of either: varchar(100)    RECEIPT;
                            RECEIPT — A flow of gas into the BB pipeline, or                        DELIVERY
                            DELIVERY — A flow of gas out of the BB
                            pipeline.
 ActualQuantity The actual flow quantity reported in TJ to the number (18,3) 32.232
                            nearest terajoule with three decimal places.                            25.2 (if Actual
