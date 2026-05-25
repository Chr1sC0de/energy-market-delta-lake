---
{
  "chunk_id": "chunk-d14b6e9ce53c72dca3bc9066",
  "chunk_ordinal": 162,
  "chunk_text_sha256": "0a882c60a10ea5b71e8551bbbdb33b6b8dd82c603cb39cb8898905f4215acdbb",
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
              "b": 75.62811279296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.42521667480469,
              "r": 527.3045043945312,
              "t": 546.4179382324219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 48
          }
        ],
        "self_ref": "#/tables/46"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-d14b6e9ce53c72dca3bc9066.md",
  "heading_path": [
    "5.1.4. INT737 - Facility Hub Capacity and Allocation Data Confirmation"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-d14b6e9ce53c72dca3bc9066.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

trading_participant_identifier, Not Null = True. trading_participant_identifier, Primary Key = False. trading_participant_identifier, Comment = The unique identifier of the trading participant. trading_participant_name, Not Null = True. trading_participant_name, Primary Key = False. trading_participant_name, Comment = The company name of the trading participant. hub_identifier, Not Null = True. hub_identifier, Primary Key = False. hub_identifier, Comment = The unique of the identifier of the hub to which the facility data relates (for example, ADL or SYD). hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub to which the facility data relates (for example, Adelaide or Sydney). facility_identifier, Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment = The unique identifier of the facility to which the capacity or allocation data relates to (for example, MAP, MSP). facility_name, Not Null = True. facility_name,
