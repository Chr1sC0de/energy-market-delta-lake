---
{
  "chunk_id": "chunk-dfdc6bac23a2a57f14e46695",
  "chunk_ordinal": 202,
  "chunk_text_sha256": "ab4fba984e01d72cd98b4b2170277d12272dc70a37df9190464dc3d667a69f9f",
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
              "b": 403.0361633300781,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.30461883544922,
              "r": 527.1575317382812,
              "t": 613.6697998046875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 63
          }
        ],
        "self_ref": "#/tables/61"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md",
    "source_manifest_line_number": 46,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-reports-specifications-v190.pdf?rev=ee0167ede9c94105b170ff3edcc2fc99&sc_lang=en"
  },
  "content_sha256": "174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_family_id": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_identity": "sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "document_title": "##### STTM Reports Specification Effective date 1 March 2021",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-dfdc6bac23a2a57f14e46695.md",
  "heading_path": [
    "5.4.4. INT654 - Provisional Market Price"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-dfdc6bac23a2a57f14e46695.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date. hub_identifier, Not Null = True. hub_identifier, Primary Key = True. hub_identifier, Comment = The unique identifier of the hub which the price relates to. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name if the hub which the price relates to.. schedule_identifier, Not Null = True. schedule_identifier, Primary Key = False. schedule_identifier, Comment = The unique identifier of the schedule which the price relates to. provisional_price, Not Null = True. provisional_price, Primary Key = False. provisional_price, Comment = The provisional price. provisional_schedule_type, Not Null = True. provisional_schedule_type, Primary Key = True. provisional_schedule_type, Comment = The type of the provisional schedule. Valid values are: • D-2 • D-3. report_datetime, Not Null = True. report_datetime, Primary Key = False. report_datetime,
