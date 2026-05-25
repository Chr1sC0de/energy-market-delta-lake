---
{
  "chunk_id": "chunk-cc25d1a7cd8fc0dfcc981183",
  "chunk_ordinal": 59,
  "chunk_text_sha256": "1bb87c6545d40590e8f50c50ef505ccc918243bf36c5518965617eee73c43eb7",
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
              "b": 94.42987060546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 102.66203308105469,
              "r": 403.2145690917969,
              "t": 224.3349609375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 15
          }
        ],
        "self_ref": "#/tables/13"
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
              "b": 736.9093873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 350.089,
              "t": 745.7108629101564
            },
            "charspan": [
              0,
              56
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/194"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/8"
        },
        "prov": [
          {
            "bbox": {
              "b": 701.749387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 518.57884,
              "t": 724.9508629101564
            },
            "charspan": [
              0,
              112
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/195"
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
              "b": 666.709387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 523.5521599999998,
              "t": 690.0308629101563
            },
            "charspan": [
              0,
              145
            ],
            "page_no": 16
          }
        ],
        "self_ref": "#/texts/196"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-cc25d1a7cd8fc0dfcc981183.md",
  "heading_path": [
    "1[2-8]((?!00000)[0-9]{5})"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-cc25d1a7cd8fc0dfcc981183.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

1, Description = Connection point identifier. 1, Values = 1. 2, Description = State code of element. 2, Values = 2 NSW and ACT 3 Victoria 4 Queensland 5 South Australia 7 Tasmania 8 Northern Territory. 3, Description = State based unique identifying number. 3, Values = 1 to 99999
Connection Point Ids have the following characteristics:
- ConnectionPointIds are defined and allocated by AEMO to BB reporting entities during the registration process.
Individual Connection Point Ids will be assigned to support each injected or withdrawn gas flow from BB pipelines and BB compression facilities .
