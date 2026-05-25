---
{
  "chunk_id": "chunk-c70615ce9e2c125acadee5a4",
  "chunk_ordinal": 356,
  "chunk_text_sha256": "af8143a8eae94767971d107f3c7607bb5e1e883cd9334dcb36b0086769ca9c56",
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
              "b": 306.87225341796875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.35104370117188,
              "r": 527.38623046875,
              "t": 749.7769470214844
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 81
          }
        ],
        "self_ref": "#/tables/112"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-c70615ce9e2c125acadee5a4.md",
  "heading_path": [
    "5.5.10. INT707 - Trading Participant Estimated Market Exposure"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28/chunk-c70615ce9e2c125acadee5a4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specifications-effective-date-3-march-2025/sha256-dcddca6ceb1ec0e7e60f8a78b66851449e589d1d335fc2d93dd1909ad9cf9a28.md"
}
---

, Not Null = . , Primary Key = . , Comment = • 'No valid guarantee'. trading_limit, Not Null = True. trading_limit, Primary Key = False. trading_limit, Comment = The trading limit for the guarantor determined from the total security amount multiplied by the trading limit percent. There will be only one trading limit per guarantor.. margin_call_limit, Not Null = True. margin_call_limit, Primary Key = False. margin_call_limit, Comment = The margin call limit being the margin call percent multiplied by the trading limit.. warning_limit, Not Null = True. warning_limit, Primary Key = False. warning_limit, Comment = The result of the trading limit multiplied by the warning limit percent. current_prudential_exposure, Not Null = True. current_prudential_exposure, Primary Key = False. current_prudential_exposure, Comment = The prudential exposure for the current billing period.. outstanding_payment, Not Null = True. outstanding_payment, Primary Key = False. outstanding_payment, Comment = The sum of the outstanding payments as determined by the prudential calculation (published statements where the 'Due Date'
