---
{
  "chunk_id": "chunk-ccb8e85cc6eba60342e630b0",
  "chunk_ordinal": 515,
  "chunk_text_sha256": "c7d9a64610654eebf3644fbd3fe2d0798d8f7ea9d253818f32fa2391c5c77004",
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
              "b": 353.5777587890625,
              "coord_origin": "BOTTOMLEFT",
              "l": 43.01650619506836,
              "r": 539.5714111328125,
              "t": 715.4456481933594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/tables/135"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ccb8e85cc6eba60342e630b0.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-ccb8e85cc6eba60342e630b0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

transmission_id Int, Data Type = transmission_id Int. transmission_id Int, No Nulls = True. transmission_id Int, Primary Key = False. transmission_id Int, CQ = N. transmission_id Int, Comments = Schedule Id Unique identifier associated with each schedule. gas_date, Data Type = varchar (20). gas_date, No Nulls = True. gas_date, Primary Key = True. gas_date, CQ = N. gas_date, Comments = Gas day os schedule. format dd mmmyyye.g. 30 Jun 2008 integer identifier of schedule of the gas day: sschedule. schedule_ interval, Data Type = Int. schedule_ interval, No Nulls = True. schedule_ interval, Primary Key = True. schedule_ interval, CQ = N. schedule_ interval, Comments = 2schedule with start time 10:00AM 3schedule with start time 2:00PM. cumulative_ price, Data Type = Numeric (15,4). cumulative_ price, No Nulls = True. cumulative_ price, Primary Key = False. cumulative_ price, CQ = N. cumulative_ price, Comments =
