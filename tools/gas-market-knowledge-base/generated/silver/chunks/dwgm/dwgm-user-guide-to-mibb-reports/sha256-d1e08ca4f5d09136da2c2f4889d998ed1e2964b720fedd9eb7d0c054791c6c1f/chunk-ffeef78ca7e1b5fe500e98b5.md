---
{
  "chunk_id": "chunk-ffeef78ca7e1b5fe500e98b5",
  "chunk_ordinal": 664,
  "chunk_text_sha256": "dc31c1a9ff45421ad2cb5ccc2ea0c90d4783d502663d32123851ec0c3b380b59",
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
              "b": 383.8175048828125,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.2513542175293,
              "r": 539.1132202148438,
              "t": 636.9839782714844
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 107
          }
        ],
        "self_ref": "#/tables/176"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ffeef78ca7e1b5fe500e98b5.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ffeef78ca7e1b5fe500e98b5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

auction_id, Data Type = INT. auction_id, No Nulls = True. auction_id, Primary Key = False. auction_id, CQ = N. auction_id, Comments = Identifier number of the CCauction. auction_date, Data Type = VARCHAR (12). auction_date, No Nulls = False. auction_date, Primary Key = False. auction_date, CQ = N. auction_date, Comments = Auction run date. dd mmmyyyy.. bid_id, Data Type = INT. bid_id, No Nulls = True. bid_id, Primary Key = True. bid_id, CQ = N. bid_id, Comments = bid identifier. zone_id, Data Type = INT. zone_id, No Nulls = True. zone_id, Primary Key = True. zone_id, CQ = N. zone_id, Comments = Identifier number of CCzone. zone_name, Data Type = NVARCHAR (50). zone_name, No Nulls = True. zone_name, Primary Key = False. zone_name, CQ = N.
