---
{
  "chunk_id": "chunk-00f7ecb982fd67bc0e68cee4",
  "chunk_ordinal": 350,
  "chunk_text_sha256": "97619345d3dfeefbef8b229413fcc4ee615634fadf8748024bb9a00430359ff1",
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
              "b": 72.03143310546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.32405853271484,
              "r": 527.4400024414062,
              "t": 599.1595306396484
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 79
          }
        ],
        "self_ref": "#/tables/109"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-00f7ecb982fd67bc0e68cee4.md",
  "heading_path": [
    "5.5.9. INT706 - Trading Participant Trading Rights v2"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-00f7ecb982fd67bc0e68cee4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

Null = True. trn_start_date, Primary Key = True. trn_start_date, Comment = The start date of the Trading Right .. trn_end_date, Not Null = True. trn_end_date, Primary Key = True. trn_end_date, Comment = The end date of the Trading Right.. contract_holder_identifier, Not Null = True. contract_holder_identifier, Primary Key = False. contract_holder_identifier, Comment = The company identifier of the contract holder.. contract_holder_name, Not Null = True. contract_holder_name, Primary Key = False. contract_holder_name, Comment = The name of the trading participant which holds the registered service the trading right relates to. allocation_agent_identifier, Not Null = False. allocation_agent_identifier, Primary Key = False. allocation_agent_identifier, Comment = The company identifier of the allocation agent if applicable. allocation_agent_name, Not Null = False. allocation_agent_name, Primary Key = False. allocation_agent_name, Comment = The company name of the allocation agent if
