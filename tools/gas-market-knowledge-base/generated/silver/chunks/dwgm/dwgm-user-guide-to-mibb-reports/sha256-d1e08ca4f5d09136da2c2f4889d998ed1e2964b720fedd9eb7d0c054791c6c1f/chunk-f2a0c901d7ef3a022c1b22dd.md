---
{
  "chunk_id": "chunk-f2a0c901d7ef3a022c1b22dd",
  "chunk_ordinal": 234,
  "chunk_text_sha256": "09e8ca3f2a4c382adb0b73fd45c6c423280aec26abc27cfcbe55a1a86a0b27de",
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
              "b": 665.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 357.23215704,
              "t": 673.5300146484376
            },
            "charspan": [
              0,
              79
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/495"
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
              "b": 647.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 420.09874077000006,
              "t": 655.5300146484376
            },
            "charspan": [
              0,
              97
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/496"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/25"
        },
        "prov": [
          {
            "bbox": {
              "b": 628.4887646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 61.515,
              "r": 239.3185401,
              "t": 636.7800146484376
            },
            "charspan": [
              0,
              49
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/497"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/25"
        },
        "prov": [
          {
            "bbox": {
              "b": 608.9887646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 61.515,
              "r": 253.79354010000003,
              "t": 617.2800146484376
            },
            "charspan": [
              0,
              50
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/498"
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
              "b": 566.2387646484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.75,
              "r": 534.48,
              "t": 597.0300146484376
            },
            "charspan": [
              0,
              278
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/499"
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
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-f2a0c901d7ef3a022c1b22dd.md",
  "heading_path": [
    "Content notes"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-f2a0c901d7ef3a022c1b22dd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

Each report confirms the details of one successfully submitted demand forecast.
Each row in the report provides the demand forecast quantity (in GJ) for one hour of the gas day:
- l ti = 1 is the first hour of the gas day (06:00)
- l ti = 2 is the second hour of the gas day (07:00)
The mod_datetime and the commencement_date should be compared against the demand forecast cut-off times specified in the market rules to determine the scheduling horizon(s) in which the submission will be used in the scheduling process (assuming there are no later submissions).
