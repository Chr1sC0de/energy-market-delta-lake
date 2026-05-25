---
{
  "chunk_id": "chunk-ef697b9a3b4c953da2c2bf1f",
  "chunk_ordinal": 309,
  "chunk_text_sha256": "e0fdd031301f1496e6863af8c869c0cc2c6cd692d0aa471d77ef0d92a1a65fcf",
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
              "b": 592.3093873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 505.0480000000001,
              "t": 613.2308629101564
            },
            "charspan": [
              0,
              96
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/texts/1412"
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
              "b": 562.0693873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 141.74,
              "r": 520.16488,
              "t": 582.9908629101564
            },
            "charspan": [
              0,
              114
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/texts/1413"
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
              "b": 544.0393873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 272.549,
              "t": 552.8408629101564
            },
            "charspan": [
              0,
              21
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/texts/1414"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/181"
        },
        "prov": [
          {
            "bbox": {
              "b": 525.9193873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 484.75899999999996,
              "t": 534.7208629101564
            },
            "charspan": [
              0,
              82
            ],
            "page_no": 82
          }
        ],
        "self_ref": "#/texts/1415"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-ef697b9a3b4c953da2c2bf1f.md",
  "heading_path": [
    "10.8.1. Modified market schedule quantities"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-ef697b9a3b4c953da2c2bf1f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

MMSQ U (p,d,k,fd) =  cf(k) {MQ U (p,d,cf(k))} + CQ U (p,d,k,fd) + FSC(p,d,k,fd) + CSC(p,d,k,fd)
For fd = 'to' there cannot be a modified market schedule quantity as STTM Users can only withdraw from the hub so:
<!-- formula-not-decoded -->
- (c) The terms MMSQ S (p,d,k,fd) and MMSQ U (p,d,k,fd) may be positive or negative.
