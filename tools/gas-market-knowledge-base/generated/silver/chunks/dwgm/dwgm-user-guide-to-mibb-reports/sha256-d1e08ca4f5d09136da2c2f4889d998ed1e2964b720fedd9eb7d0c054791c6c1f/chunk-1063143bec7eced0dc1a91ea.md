---
{
  "chunk_id": "chunk-1063143bec7eced0dc1a91ea",
  "chunk_ordinal": 1217,
  "chunk_text_sha256": "2b86f6cd33ed4f3ace7894c2656b3f09c3bb92ca1bfaae638f70b4ce0e680d50",
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
              "b": 448.383544921875,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.172977447509766,
              "r": 538.9649047851562,
              "t": 627.1787872314453
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 187
          }
        ],
        "self_ref": "#/tables/359"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1063143bec7eced0dc1a91ea.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-1063143bec7eced0dc1a91ea.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

mirn, Data Type = varchar 10. mirn, No Nulls = True. mirn, Primary Key = True. mirn, CQ = N. mirn, Comments = Vic gas equivalent to National Meter Identifier (NMI). gas_date, Data Type = varchar 20. gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Gas day the status of the MIRN changed e.g. 30 Jun 2007. movement, Data Type = char 5.. movement, No Nulls = False. movement, Primary Key = True. movement, CQ = CQ. movement, Comments = Won or Lost or None. status_type, Data Type = char 15.. status_type, No Nulls = True. status_type, Primary Key = True. status_type, CQ = CQ. status_type, Comments = Registered (ie Decommissioned or never been Commissioned). tariff_type, Data Type = char 1. tariff_type, No Nulls = True. tariff_type, Primary Key = False. tariff_type, CQ = . tariff_type,
