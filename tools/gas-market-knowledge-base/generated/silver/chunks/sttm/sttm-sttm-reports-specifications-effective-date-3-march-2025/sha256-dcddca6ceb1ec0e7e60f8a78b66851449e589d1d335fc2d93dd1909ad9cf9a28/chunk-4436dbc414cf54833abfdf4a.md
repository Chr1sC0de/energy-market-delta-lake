---
{
  "chunk_id": "chunk-4436dbc414cf54833abfdf4a",
  "chunk_ordinal": 162,
  "chunk_text_sha256": "2535e140cb1d562f1f04fbdd6287e865701d02a9e6c57dadb2b1f3ee1cd43be9",
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
        "children": [],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 141.335693359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.2916259765625,
              "r": 527.592529296875,
              "t": 750.1739273071289
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/tables/41"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md",
    "source_manifest_line_number": 47,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-reports-specifications-v191.pdf?rev=30dbf1c556a7486b8c80e244b8690226&sc_lang=en"
  },
  "content_sha256": "dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specifications-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-reports-specifications-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28",
  "document_title": "##### STTM Reports Specifications Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-4436dbc414cf54833abfdf4a.md",
  "heading_path": [
    "5.3.2. INT721A - Active Pipeline Operator MOS Stack"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-4436dbc414cf54833abfdf4a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

contract holder's organisation name. step_quantity, Not Null = True. step_quantity, Primary Key = False. step_quantity, Comment = The quantity of gas associated with this MOS stack step as submitted by the MOS provider. This is the maximum quantity that can be allocated to this MOS stack step during the allocation process after the gas day by the Pipeline Operator.. step_price, Not Null = True. step_price, Primary Key = False. step_price, Comment = The price submitted by the MOS provider for MOS gas called in this step.. facility_contract_reference_t o_the_hub, Not Null = False. facility_contract_reference_t o_the_hub, Primary Key = False. facility_contract_reference_t o_the_hub, Comment = The facility external reference provided by the pipeline operator to the MOS provider and used by the MOS provider to indicate the "to the hub" facility contract the pipeline operator is to associate with this step if the step is called. Either this field or facility_contract_reference_from_the_hub may be. facility_contract_reference_fr om_the_hub, Not Null = False.
