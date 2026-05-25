---
{
  "chunk_id": "chunk-1bdfef02c073f434a198b6d4",
  "chunk_ordinal": 89,
  "chunk_text_sha256": "6ff844809804322c5139d2ea6749f7e7167eef55711c57385fe2a5bd57010341",
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
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 488.359387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 374.56899999999996,
              "t": 497.1608629101563
            },
            "charspan": [
              0,
              54
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/318"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 467.599387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 440.929,
              "t": 476.40086291015626
            },
            "charspan": [
              0,
              74
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/319"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 446.959387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 341.089,
              "t": 455.7608629101563
            },
            "charspan": [
              0,
              51
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/320"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 426.199387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 367.00899999999996,
              "t": 435.0008629101563
            },
            "charspan": [
              0,
              55
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/321"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/23"
        },
        "prov": [
          {
            "bbox": {
              "b": 390.919387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 523.159,
              "t": 414.2408629101563
            },
            "charspan": [
              0,
              178
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/322"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-1bdfef02c073f434a198b6d4.md",
  "heading_path": [
    "4.3.3. Validation rules"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-1bdfef02c073f434a198b6d4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

- Gas Date must conform to the date format YYYY-MM-DD.
- Submissions must only contain Facility Ids registered to the Company Id.
- Negative Actual Quantity values are not accepted.
- NegativeCushion Gas Quantity values are not accepted.
- CushionGasQuantity validates against Storage Nameplate Rating i.e.: CushionGasQuantity must be less than or equal to facility Nameplate rating where CapacityType equals Storage
