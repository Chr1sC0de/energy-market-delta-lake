---
{
  "chunk_id": "chunk-9c13d71f58ce1a4294e19cee",
  "chunk_ordinal": 785,
  "chunk_text_sha256": "65eb52fe64ce4bd74ae9104740e49be7b3a73dc1a9c99922cd3c4618c0e74c3f",
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
              "b": 312.4837646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 529.4549999999999,
              "t": 332.0250146484375
            },
            "charspan": [
              0,
              228
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/texts/1830"
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
              "b": 294.4837646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 286.70666931000005,
              "t": 302.7750146484375
            },
            "charspan": [
              0,
              64
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/texts/1831"
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
              "b": 276.4837646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 348.50959956,
              "t": 284.7750146484375
            },
            "charspan": [
              0,
              81
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/texts/1832"
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
              "b": 247.2337646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 515.6624999999999,
              "t": 266.7750146484375
            },
            "charspan": [
              0,
              165
            ],
            "page_no": 124
          }
        ],
        "self_ref": "#/texts/1833"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-9c13d71f58ce1a4294e19cee.md",
  "heading_path": [
    "Report purpose"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-9c13d71f58ce1a4294e19cee.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

This report is a comma separated values (csv) file that provides a snapshot of the meter register and data used in producing settlement statements. A version of the report is produced each time a settlement version is generated.
The report has the full set of gas days in the settlement month.
This report is similar to INT055 which covers details of meter registration data.
Please note that this report will only display AMDQ information up until gas day: 31 Dec 2022. From gas day 1 Jan 2023, AMDQ will not be used for Uplift calculation.
