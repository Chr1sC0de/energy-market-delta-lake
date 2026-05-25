---
{
  "chunk_id": "chunk-d9cc44a9e08db3827b1caef5",
  "chunk_ordinal": 769,
  "chunk_text_sha256": "a625fdb654fe37a13ba4426093cacf9e56f641d9bec8c8f7ff965234d6cb3be6",
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
              "b": 688.4887646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 537.0074999999999,
              "t": 753.0300146484376
            },
            "charspan": [
              0,
              663
            ],
            "page_no": 122
          }
        ],
        "self_ref": "#/texts/1799"
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
              "b": 659.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 515.6624999999999,
              "t": 678.7800146484376
            },
            "charspan": [
              0,
              165
            ],
            "page_no": 122
          }
        ],
        "self_ref": "#/texts/1800"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-d9cc44a9e08db3827b1caef5.md",
  "heading_path": [
    "Report purpose"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-d9cc44a9e08db3827b1caef5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

This report is a comma separated values (csv) file that contains details of interval meters stored in AEMO's meter register and assigned to a specific participant. Participants may wish to use this report to validate AEMO's records of their customers and the parameters associated with each site. This information is valuable as a source to reconcile wholesale settlement values and to validate the outcomes of customer transfer activities. This version of the report is produced daily and reflects changes resulting from overnight CATS processing of transfers from pending to complete. Section 4.6 and 4.7 of the RMP describes transfer registration requirements.
Please note that this report will only display AMDQ information up until gas day: 31 Dec 2022. From gas day 1 Jan 2023, AMDQ will not be used for Uplift calculation.
