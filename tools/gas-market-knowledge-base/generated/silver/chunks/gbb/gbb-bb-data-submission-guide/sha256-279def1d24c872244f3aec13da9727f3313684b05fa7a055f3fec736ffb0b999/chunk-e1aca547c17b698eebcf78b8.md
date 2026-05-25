---
{
  "chunk_id": "chunk-e1aca547c17b698eebcf78b8",
  "chunk_ordinal": 179,
  "chunk_text_sha256": "36331b5df05b0bdbe98087d3c75f17c45dfa5f26a3f94b20369606d090769966",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/49"
        },
        "prov": [
          {
            "bbox": {
              "b": 274.619387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 382.969,
              "t": 283.4208629101563
            },
            "charspan": [
              0,
              56
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/599"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/49"
        },
        "prov": [
          {
            "bbox": {
              "b": 253.85938739080802,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 414.529,
              "t": 262.6608629101563
            },
            "charspan": [
              0,
              63
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/600"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/49"
        },
        "prov": [
          {
            "bbox": {
              "b": 233.09938739080803,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 410.68899999999996,
              "t": 241.90086291015632
            },
            "charspan": [
              0,
              61
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/601"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/49"
        },
        "prov": [
          {
            "bbox": {
              "b": 212.33938739080804,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 323.789,
              "t": 221.14086291015633
            },
            "charspan": [
              0,
              47
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/602"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/49"
        },
        "prov": [
          {
            "bbox": {
              "b": 191.57938739080805,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 332.909,
              "t": 200.38086291015634
            },
            "charspan": [
              0,
              49
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/603"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md",
    "source_manifest_line_number": 12,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-gbb-procedures-for-renewable-gas/decision/bb-data-submission-guide-v21.pdf?rev=1890be0ffbbe470d9694e56288a8df59&sc_lang=en"
  },
  "content_sha256": "279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999",
  "corpus": "gbb",
  "document_family": "gbb__bb-data-submission-guide",
  "document_family_id": "gbb__bb-data-submission-guide",
  "document_identity": "gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999",
  "document_title": "##### BB Data Submission Guide",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-e1aca547c17b698eebcf78b8.md",
  "heading_path": [
    "4.16.3. Validation rules"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-e1aca547c17b698eebcf78b8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

- Trade Date must conform to the date format YYYY-MM-DD.
- SupplyPeriodStart must conform to the date format YYYY-MM-DD.
- SupplyPeriodEnd must conform to the date format YYYY-MM-DD.
- Volume must be greater than or equal to zero.
- FOBPrice must be greater than or equal to zero.
