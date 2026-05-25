---
{
  "chunk_id": "chunk-6bdba732cf2dc097d03961fe",
  "chunk_ordinal": 149,
  "chunk_text_sha256": "4258df5f7868fa10e27fd59be3d0383fde7e65a05b6298025d9e8060d910cdb9",
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
          "$ref": "#/groups/39"
        },
        "prov": [
          {
            "bbox": {
              "b": 354.899387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 523.8291199999998,
              "t": 392.7608629101563
            },
            "charspan": [
              0,
              198
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/514"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/39"
        },
        "prov": [
          {
            "bbox": {
              "b": 305.2193873908079,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 494.36743999999993,
              "t": 342.9408629101563
            },
            "charspan": [
              0,
              187
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/515"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/39"
        },
        "prov": [
          {
            "bbox": {
              "b": 269.93938739080795,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 504.7756399999997,
              "t": 293.2608629101562
            },
            "charspan": [
              0,
              104
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/516"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/39"
        },
        "prov": [
          {
            "bbox": {
              "b": 249.17938739080796,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 308.669,
              "t": 257.98086291015625
            },
            "charspan": [
              0,
              42
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/517"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/39"
        },
        "prov": [
          {
            "bbox": {
              "b": 228.41938739080797,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 299.30899999999997,
              "t": 237.22086291015626
            },
            "charspan": [
              0,
              43
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/518"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-6bdba732cf2dc097d03961fe.md",
  "heading_path": [
    "4.10.2. Validation rules"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-6bdba732cf2dc097d03961fe.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

- Delivery and Receipt Point Ids must be valid within the registered list of service points in the transportation service point register established under Part 24 where the Facility Id is populated.
- Park Loan Point Ids must be valid within the registered list of service points in the transportation service point register established under Part 24 where the Facility Id is populated.
- Facility Name and Flow Direction must be populated where the Facility is not registered under Part 24.
- Quantity and MHQ must be greater than 0.
- Price must be equal to or greater than 0.
