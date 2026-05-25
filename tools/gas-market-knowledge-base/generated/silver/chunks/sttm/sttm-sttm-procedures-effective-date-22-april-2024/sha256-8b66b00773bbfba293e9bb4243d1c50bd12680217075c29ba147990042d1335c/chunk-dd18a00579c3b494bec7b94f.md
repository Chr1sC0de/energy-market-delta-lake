---
{
  "chunk_id": "chunk-dd18a00579c3b494bec7b94f",
  "chunk_ordinal": 282,
  "chunk_text_sha256": "a3219e0aa41a8020b90af5af1fd6979b43c5fa608e224d79d41cc34ed1a1b3bb",
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
              "b": 669.1388423806247,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 529.5910000000005,
              "t": 703.2519829101564
            },
            "charspan": [
              0,
              284
            ],
            "page_no": 75
          }
        ],
        "self_ref": "#/texts/1263"
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
              "b": 624.0188423806247,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 519.9940000000001,
              "t": 658.1319829101564
            },
            "charspan": [
              0,
              281
            ],
            "page_no": 75
          }
        ],
        "self_ref": "#/texts/1264"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/154"
        },
        "prov": [
          {
            "bbox": {
              "b": 589.3093873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 502.86064,
              "t": 612.6308629101563
            },
            "charspan": [
              0,
              130
            ],
            "page_no": 75
          }
        ],
        "self_ref": "#/texts/1265"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "formula",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 556.1593873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 525.8771200000001,
              "t": 577.9479829101564
            },
            "charspan": [
              0,
              152
            ],
            "page_no": 75
          }
        ],
        "self_ref": "#/texts/1266"
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
              "b": 513.1088423806248,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 529.5880000000006,
              "t": 547.2219829101563
            },
            "charspan": [
              0,
              284
            ],
            "page_no": 75
          }
        ],
        "self_ref": "#/texts/1267"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md",
    "source_manifest_line_number": 44,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/sttm-procedures/sttm-procedures-v135.pdf?rev=93f1f406f57a41dab9175821eea6c334&sc_lang=en"
  },
  "content_sha256": "8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-22-april-2024",
  "document_family_id": "sttm__sttm-procedures-effective-date-22-april-2024",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c",
  "document_title": "##### STTM Procedures Effective date 22 April 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-dd18a00579c3b494bec7b94f.md",
  "heading_path": [
    "Explanatory Note"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-dd18a00579c3b494bec7b94f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

Note : The quantities in these equations are the changes to scheduled flows due to contingency gas being called which increase the quantity shipped to the hub or decrease the quantity withdrawn from the hub .  The latter quantities are negative, so must be multiplied by negative one.
This section relates to contingency gas usage producing positive changes in flows to the hub and negative changes in flows from the hub .  The MAX() functions in the following equations extract either the positive or negative changes as required and convert it to a positive value.
- (b) The charge payable by Trading Participant p for gas day d when contingency gas is called to decrease net supply to the hub is:
<!-- formula-not-decoded -->
Note : The quantities in these equations are the changes to scheduled flows due to contingency gas being called which decrease the quantity shipped to the hub or increase the quantity withdrawn from the hub .  The former quantities are negative, so must be multiplied by negative one.
