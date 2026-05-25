---
{
  "chunk_id": "chunk-cad4ad184c95b7337846dd9b",
  "chunk_ordinal": 1350,
  "chunk_text_sha256": "953085ca696e8c38600ee0d03858b43e51e54a2b9d6d8dce68e4554abf09c215",
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
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 340.2337646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 526.6274999999999,
              "t": 359.7750146484375
            },
            "charspan": [
              0,
              181
            ],
            "page_no": 205
          }
        ],
        "self_ref": "#/texts/3231"
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
              "b": 299.7337646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 540.165,
              "t": 330.5250146484375
            },
            "charspan": [
              0,
              347
            ],
            "page_no": 205
          }
        ],
        "self_ref": "#/texts/3232"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-cad4ad184c95b7337846dd9b.md",
  "heading_path": [
    "Report purpose"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-cad4ad184c95b7337846dd9b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

Once a ROLR event has occurred and AEMO has completed updates to its Meter Register, AEMO provides the below data (equivalent to MIBB report INT055) to each of the designated ROLRs.
This is a Market participant specific report, produced once after a ROLR event. Note: 1 mdq_site field. This is used by the uplift calculation where at one site multiple mirns exist. It indicates the parent mirn of the site that the mirn is being assigned to for the calculation. For sites with only one mirn the site code is the same as the MIRN.
