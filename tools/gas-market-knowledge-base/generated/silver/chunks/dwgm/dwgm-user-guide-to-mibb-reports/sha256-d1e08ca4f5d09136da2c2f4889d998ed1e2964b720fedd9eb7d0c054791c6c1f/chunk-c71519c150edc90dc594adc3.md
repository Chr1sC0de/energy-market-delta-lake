---
{
  "chunk_id": "chunk-c71519c150edc90dc594adc3",
  "chunk_ordinal": 419,
  "chunk_text_sha256": "9843c715306110d3c8452901c80ada9d737c44642795db9b45e5768615a62e70",
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
              "b": 403.4887646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 535.0649999999999,
              "t": 445.5300146484376
            },
            "charspan": [
              0,
              385
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/994"
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
              "b": 374.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 525.2175,
              "t": 393.7800146484376
            },
            "charspan": [
              0,
              194
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/995"
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
              "b": 344.9887646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 527.5949999999999,
              "t": 364.5300146484375
            },
            "charspan": [
              0,
              133
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/996"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-c71519c150edc90dc594adc3.md",
  "heading_path": [
    "Some reports provide information only for the next gas day (not 2 days into the future)."
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-c71519c150edc90dc594adc3.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

The number of gas days and/or schedules covered by a report will depend on the time at which the particular report version is produced. In general, reports produced by the approval of standard schedules at 06:00   AM and 10:00   AM will contain information only for the past 7, current and next gas day as at that point in time no schedules for 2 days in the future will have been run.
For the section of the report providing information on linepack minima (rows where type = 'LPMIN'), there is one row for the system linepack minimum for each gas day within the reporting window.
For the section of the report providing information on hourly scheduled linepack quantities (rows where type = 'LPSCHED'), there are:
