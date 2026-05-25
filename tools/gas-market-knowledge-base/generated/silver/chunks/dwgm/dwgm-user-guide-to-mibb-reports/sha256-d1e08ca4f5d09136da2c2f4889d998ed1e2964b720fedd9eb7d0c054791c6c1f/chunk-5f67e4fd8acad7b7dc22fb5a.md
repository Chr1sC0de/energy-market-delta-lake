---
{
  "chunk_id": "chunk-5f67e4fd8acad7b7dc22fb5a",
  "chunk_ordinal": 44,
  "chunk_text_sha256": "92323556c76f45730fe5ea14b6140166707771cc0ae666f64e595124d2fe9cbf",
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
              "b": 507.7387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 540.3,
              "t": 549.7800146484376
            },
            "charspan": [
              0,
              403
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/90"
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
              "b": 478.4887646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 528.57718158,
              "t": 498.0300146484376
            },
            "charspan": [
              0,
              152
            ],
            "page_no": 13
          }
        ],
        "self_ref": "#/texts/91"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-5f67e4fd8acad7b7dc22fb5a.md",
  "heading_path": [
    "Hour columns"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-5f67e4fd8acad7b7dc22fb5a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

Where only the hour or time interval (ti) is required, the column name should include hour or hr using the 24-hour clock format. Columns should be numbered from 1 to 24. Time is displayed as an offset -1 from any associated date column. For example, in a report with a gas_date column with hour columns, the hours columns represent 6.00 AM for hour_1 if the gas_date column has a 6.00 AM time component.
If the actual hour is required, the column should be named with the AMPM indicator and start at 6:00 AM; for example, hour_ 9am, hour_10am, …, hour_8am.
