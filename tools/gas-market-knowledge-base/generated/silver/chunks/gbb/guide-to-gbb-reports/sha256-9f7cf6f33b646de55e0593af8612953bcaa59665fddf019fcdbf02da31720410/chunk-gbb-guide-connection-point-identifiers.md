---
{
  "chunk_id": "chunk-gbb-guide-connection-point-identifiers",
  "chunk_ordinal": 2,
  "chunk_text_sha256": "300b4b97b9570ffe501b2942fdcf892e64eba0c68ebfa405b65134a7b31899d2",
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
        "source_text_line_end": 359,
        "source_text_line_start": 328
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
  "generated_path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-connection-point-identifiers.md",
  "heading_path": [
    "Guide to Gas Bulletin Board Reports",
    "Connection point identifiers"
  ],
  "path": "generated/silver/chunks/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410/chunk-gbb-guide-connection-point-identifiers.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/guide-to-gbb-reports/sha256-9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410.md"
}
---

Guide to Gas Bulletin Board Reports

        For example, FacilityId “520345” relates to an element (BB reporting entity) within NSW and
        ACT with a unique identifier of “0345” which is related to the gas industry.

2.2.2. Connection Point Identifiers

        Connection Point identifiers (ConnectionPointId) used in transactions and reports subscribe to
        the following format:
 1+[2-8]+[0-9]{1,5}

 Item Description Values
 1 Connection point identifier 1
 2 State code of element 2 NSW and ACT
                                                               3 Victoria
                                                               4 Queensland
                                                               5 South Australia
                                                               7 Tasmania
                                                               8 Northern Territory
 3 State based unique identifying number 1 to 99999

        ConnectionPointIDs have the following characteristics:

        • ConnectionPointIDs are defined and allocated by AEMO to BB reporting entities during the
          registration process.

        • A unique ConnectionPointID will be assigned for each receipt and delivery gas flow for each
          registered facility.
