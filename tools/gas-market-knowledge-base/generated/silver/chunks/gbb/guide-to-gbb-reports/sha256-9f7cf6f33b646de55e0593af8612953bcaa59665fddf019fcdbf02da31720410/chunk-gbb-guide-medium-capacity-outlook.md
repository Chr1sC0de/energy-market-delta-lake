---
{
  "chunk_id": "chunk-gbb-guide-medium-capacity-outlook",
  "chunk_ordinal": 5,
  "chunk_text_sha256": "232731bf738451672e8f3ac08cb83a65d05f42c1226d0326d2db95597d61f339",
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
        "source_text_line_end": 775,
        "source_text_line_start": 725
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
  "generated_path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-medium-capacity-outlook.md",
  "heading_path": [
    "Guide to Gas Bulletin Board Reports",
    "Medium term capacity outlook report"
  ],
  "path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-medium-capacity-outlook.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md"
}
---

AEMO | 3 March 2025                                                                                                        Page 14 of 45

Guide to Gas Bulletin Board Reports

4.4.3. Example report
           Vist the AEMO developer portal for example for HTTPS GET request examples.

4.5. Medium Term Capacity Outlook
4.5.1. Description
 Transaction report GASBB_MEDIUM_TERM _OUTLOOK_FULL_LIST / GASBB_MEDIUM_TERM
 name _OUTLOOK_FUTURE
 Purpose                Provides a report of the Capacity Outlook for the medium term to identify possible impact to future
                        supply.
 Production GASBB_MEDIUM_TERM _OUTLOOK_FULL_LIST is updated daily /
 frequency GASBB_MEDIUM_TERM _OUTLOOK_FUTURE is updated within 30 minutes of receiving new data.
 Report period GASBB_MEDIUM_TERM _OUTLOOK_FULL_LIST contains historic and future outlooks /
                        GASBB_MEDIUM_TERM _OUTLOOK_FUTURE contains the current and future outlooks.

4.5.2. Data report format

           The following fields are provided in the report.

 Field name Description Data type Example
 FacilityId Unique plant identifier.                                Int                520345
 FacilityName Name of the plant. varchar(255) Berwyndale to
                                                                                                       Wallumbilla Pipeline
 FromGasDate                Date of gas day. Any time component supplied is datetime 2018-09-23
                            ignored. The gas day is applicable under the
                            pipeline contract or market rules.
 ToGasDate Date of gas day. Any time component supplied is datetime 2018-09-23
                            ignored. The gas day is that applicable under the
                            pipeline contract or market rules.
 CapacityType Capacity type values can be:                            varchar(20)        STORAGE; MDQ
                            STORAGE — Holding capacity in storage; or
                            MDQ — Daily maximum firm capacity under the
                            expected operating conditions.
 OutlookQuantity            Capacity outlook quantity in TJ to three decimal        number(18,3) 200.531
                            places. Three decimal places is not required if the                        190.2 (if the value is
                            value has trailing zeros after the decimal place. 190.200)

 FlowDirection Gas flow direction. Values can be either: char(20) RECEIPT; DELIVERY;
                            Receipt: The flow of gas into the BB storage facility PROCESSED;
