---
{
  "chunk_id": "chunk-1d5a72bc38875b5c5470febb",
  "chunk_ordinal": 188,
  "chunk_text_sha256": "6de59c5c4552e63d5433ebb1657ac3d7b1d518e53bbeb0679a5c8203461ffc0d",
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
              "b": 106.064208984375,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.55624389648438,
              "r": 527.2853393554688,
              "t": 585.7232055664062
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 57
          }
        ],
        "self_ref": "#/tables/55"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-1d5a72bc38875b5c5470febb.md",
  "heading_path": [
    "5.4.1. INT651 - Ex Ante Market Price"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-1d5a72bc38875b5c5470febb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date eg 30 Jun 2009. hub_identifier, Not Null = True. hub_identifier, Primary Key = True. hub_identifier, Comment = The unique identifer of the hub. hub_name, Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub. schedule_identifier, Not Null = False. schedule_identifier, Primary Key = False. schedule_identifier, Comment = The unique identifier of the schedule which the ex ante market price relates to, with the exception of where the administered_price_period is equal to 'Y'. ex_ante_market_price, Not Null = True. ex_ante_market_price, Primary Key = False. ex_ante_market_price, Comment = The ex ante market price for the gas date. This price is either the market price determined by the scheduling and pricing engine or the administered price during an administered price period.. administered_price_period, Not Null = True.
