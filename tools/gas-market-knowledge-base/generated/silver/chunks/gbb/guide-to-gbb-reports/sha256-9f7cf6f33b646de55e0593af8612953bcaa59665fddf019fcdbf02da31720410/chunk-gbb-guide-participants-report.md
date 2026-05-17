---
{
  "chunk_id": "chunk-gbb-guide-participants-report",
  "chunk_ordinal": 4,
  "chunk_text_sha256": "31d24c051f2967ba12eff0c5e21d452361a96d7cced92c7a693b460760d61873",
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
        "source_text_line_end": 1170,
        "source_text_line_start": 1146
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
  "generated_path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-participants-report.md",
  "heading_path": [
    "Guide to Gas Bulletin Board Reports",
    "Participants report"
  ],
  "path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-participants-report.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md"
}
---

AEMO | 3 March 2025                                                                                       Page 20 of 45

Guide to Gas Bulletin Board Reports

 Field name Description Data type Example
 PersonId Person unique identifier Int            123456
 PersonName Name of the person                                varchar(255) John Smith
 CompanyName Company name associated with the person. varchar(050) Bolder Mining Company
 CompanyId            Company ID associated with the person Int            13
 Position Job title of person. varchar(40)    Energy Procurement Manager
 Email                Email address of person. varchar(255) <john.smith@boldermining.com.au>
 Last Updated Date and time the record was last modified. datetime 2018-08-14

4.9.3. Example report
            Vist the AEMO developer portal for example for HTTPS GET request examples.

4.10. Participants
4.10.1. Description
 Transaction report GASBB_PARTICIPANTS_LIST
 name
 Purpose Provides a report of registered participants
