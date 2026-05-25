---
{
  "chunk_id": "chunk-deaed3c2cfd6e6555df0bacd",
  "chunk_ordinal": 156,
  "chunk_text_sha256": "77e8410cbb393577dc9f686eb48c6de63496b6e0f2dedb8ac219b7273ea4eed5",
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
          "$ref": "#/groups/42"
        },
        "prov": [
          {
            "bbox": {
              "b": 496.159387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 492.31647999999996,
              "t": 519.4808629101564
            },
            "charspan": [
              0,
              160
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/texts/537"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/42"
        },
        "prov": [
          {
            "bbox": {
              "b": 475.399387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 482.599,
              "t": 484.2008629101563
            },
            "charspan": [
              0,
              83
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/texts/538"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/42"
        },
        "prov": [
          {
            "bbox": {
              "b": 440.119387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 521.1965600000001,
              "t": 463.4408629101563
            },
            "charspan": [
              0,
              105
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/texts/539"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/42"
        },
        "prov": [
          {
            "bbox": {
              "b": 404.839387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 498.74752,
              "t": 428.1608629101563
            },
            "charspan": [
              0,
              145
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/texts/540"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-deaed3c2cfd6e6555df0bacd.md",
  "heading_path": [
    "4.13.2. Requirements"
  ],
  "path": "generated/silver/chunks/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999/chunk-deaed3c2cfd6e6555df0bacd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-bb-data-submission-guide/sha256-279def1d24c872244f3aec13da9727f3313684b05fa7a055f3fec736ffb0b999.md"
}
---

- BB storage , BB compression , and BB pipeline facility types must report the list of BB shippers who have contracted primary firm capacity on the BB facility.
- Each Submission must contain a complete list of Shippers for each effective date.
- If there are no BB shippers on a facility, a submission must still be made with ShipperName field empty
- If a future list is no longer relevant, a new submission with the same effective date and correct BB shippers should be submitted in its place.
