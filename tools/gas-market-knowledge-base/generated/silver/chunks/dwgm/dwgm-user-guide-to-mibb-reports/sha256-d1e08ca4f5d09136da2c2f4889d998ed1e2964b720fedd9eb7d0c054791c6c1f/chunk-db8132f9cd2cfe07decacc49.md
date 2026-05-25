---
{
  "chunk_id": "chunk-db8132f9cd2cfe07decacc49",
  "chunk_ordinal": 705,
  "chunk_text_sha256": "95e1e76d1d21ccca170d8bd422daaab15a4ea32a03b940cb265ea1536322aac5",
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
              "b": 115.6795654296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.279850006103516,
              "r": 539.7083129882812,
              "t": 368.6404724121094
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 112
          }
        ],
        "self_ref": "#/tables/188"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 113.7337646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 107.96249999999999,
              "r": 131.47316958,
              "t": 122.02501464843749
            },
            "charspan": [
              0,
              6
            ],
            "page_no": 112
          }
        ],
        "self_ref": "#/texts/1634"
      },
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
              "b": 679.2911987304688,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.25972366333008,
              "r": 539.0436401367188,
              "t": 769.9589691162109
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 113
          }
        ],
        "self_ref": "#/tables/189"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md",
    "source_manifest_line_number": 4,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/april-2024-amendment-to-user-guide-to-mibb-reports/user-guide-to-mibb-reports.pdf?rev=b5b659bce66a4808b505db05ecb0ca13&sc_lang=en"
  },
  "content_sha256": "d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "corpus": "dwgm",
  "document_family": "dwgm__user-guide-to-mibb-reports",
  "document_family_id": "dwgm__user-guide-to-mibb-reports",
  "document_identity": "dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "document_title": "##### User Guide to MIBB Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-db8132f9cd2cfe07decacc49.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-db8132f9cd2cfe07decacc49.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

capacity.. bid_id, Data Type = INT. bid_id, No Nulls = True. bid_id, Primary Key = True. bid_id, CQ = N. bid_id, Comments = bid identifier. clearing_price, Data Type = NUMERIC. clearing_price, No Nulls = False. clearing_price, Primary Key = False. clearing_price, CQ = Y. clearing_price, Comments = Price in which bid cleared.
(15,4)
quantities_ won_gj, Data Type = NUMERIC (18,9). quantities_ won_gj, No Nulls = False. quantities_ won_gj, Primary Key = False. quantities_ won_gj, CQ = Y. quantities_ won_gj, Comments = Quantity won in GJ. current_date, Data Type = VARCHAR (12). current_date, No Nulls = True. current_date, Primary Key = False. current_date, CQ = N. current_date, Comments = Report generation date. dd mmmyyyy hh:mm:ss
