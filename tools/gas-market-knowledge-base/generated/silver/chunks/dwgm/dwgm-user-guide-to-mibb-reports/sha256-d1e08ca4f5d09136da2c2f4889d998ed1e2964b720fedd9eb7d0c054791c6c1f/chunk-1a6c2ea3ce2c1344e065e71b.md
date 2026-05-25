---
{
  "chunk_id": "chunk-1a6c2ea3ce2c1344e065e71b",
  "chunk_ordinal": 1139,
  "chunk_text_sha256": "dd1aaa0bc5b9e67e5dfd3734ebfc8f5e09ef299cc1cce025a3c91b5b53c936fa",
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
              "b": 514.2408447265625,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.290771484375,
              "r": 539.5492553710938,
              "t": 769.7617874145508
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 176
          }
        ],
        "self_ref": "#/tables/333"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1a6c2ea3ce2c1344e065e71b.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1a6c2ea3ce2c1344e065e71b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

to_date, Data Type = varchar (12). to_date, No Nulls = False. to_date, Unique Key = False. to_date, CQ = N. to_date, Comments = The last gas date (if any) to which the current row's details apply in the format dd mon yyyy.. type_desc, Data Type = varchar (250). type_desc, No Nulls = False. type_desc, Unique Key = True. type_desc, CQ = N. type_desc, Comments = Applicable billing period for settlements (PRL, FNL or REV) Bank Guarantee details for security amounts (GUARANTEE). pmt_amt_ from_aemo, Data Type = numeric (15,2). pmt_amt_ from_aemo, No Nulls = False. pmt_amt_ from_aemo, Unique Key = False. pmt_amt_ from_aemo, CQ = N. pmt_amt_ from_aemo, Comments = Payment held/received by AEMOor owed to the participant. (Includes both prepayments and
