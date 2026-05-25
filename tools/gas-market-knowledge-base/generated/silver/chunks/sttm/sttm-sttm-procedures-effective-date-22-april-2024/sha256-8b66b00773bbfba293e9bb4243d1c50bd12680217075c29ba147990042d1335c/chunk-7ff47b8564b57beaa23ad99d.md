---
{
  "chunk_id": "chunk-7ff47b8564b57beaa23ad99d",
  "chunk_ordinal": 257,
  "chunk_text_sha256": "11d439de1b1bf3fbfac06fd4025e3bfc44167a8390aba8093683d26409095319",
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
              "b": 461.38884238062474,
              "coord_origin": "BOTTOMLEFT",
              "l": 73.464,
              "r": 523.8400000000001,
              "t": 534.6219829101564
            },
            "charspan": [
              0,
              626
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/1155"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/140"
        },
        "prov": [
          {
            "bbox": {
              "b": 418.639387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 494.359,
              "t": 427.4408629101563
            },
            "charspan": [
              0,
              86
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/1156"
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
              "b": 397.999387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 382.969,
              "t": 406.8008629101563
            },
            "charspan": [
              0,
              54
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/1157"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/141"
        },
        "prov": [
          {
            "bbox": {
              "b": 379.879387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 486.919,
              "t": 388.6808629101563
            },
            "charspan": [
              0,
              85
            ],
            "page_no": 69
          }
        ],
        "self_ref": "#/texts/1158"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-7ff47b8564b57beaa23ad99d.md",
  "heading_path": [
    "Explanatory Note"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-7ff47b8564b57beaa23ad99d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

This clause describes how AEMO determines the ex ante market payment and ex ante market charge for a Trading Participant at a hub for a gas day for the purposes of rule 461(2)(a).  The ex ante market payment is determined in accordance with clause 10.3(a), by multiplying the ex ante market price by the sum of that Trading Participant 's market schedule quantities for the supply of gas to the hub .  The ex ante market charge is determined in accordance with clause 10.3(b), by multiplying the ex ante market price by the sum of that Trading Participant 's market schedule quantities for the withdrawal of gas from the hub .
- (a) The ex ante market payment for Trading Participant p for gas day d for the hub is:
MktP(p,d) =  HP(d) ×  k  SP  ct(k) MQ S (p,d,ct(k))
- (b) The ex ante market charge for Trading Participant p for gas day d for the hub is:
