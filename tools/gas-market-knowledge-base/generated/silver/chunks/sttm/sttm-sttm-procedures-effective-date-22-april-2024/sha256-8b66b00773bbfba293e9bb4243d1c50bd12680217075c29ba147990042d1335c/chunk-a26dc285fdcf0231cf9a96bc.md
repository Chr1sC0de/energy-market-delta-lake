---
{
  "chunk_id": "chunk-a26dc285fdcf0231cf9a96bc",
  "chunk_ordinal": 334,
  "chunk_text_sha256": "c6ac967a7cce5a9b063c64c163964daa9d2de98b68f4793f20cc9ce1425f83c8",
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
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 511.39938739080804,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 457.849,
              "t": 593.4308629101563
            },
            "charspan": [
              0,
              374
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/texts/1554"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "code",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 511.39938739080804,
              "coord_origin": "BOTTOMLEFT",
              "l": 221.57,
              "r": 510.07899999999995,
              "t": 656.7908629101563
            },
            "charspan": [
              0,
              76
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/texts/1555"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-a26dc285fdcf0231cf9a96bc.md",
  "heading_path": [
    "10.10.2. Billing period deviation quantities"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-a26dc285fdcf0231cf9a96bc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

```
If DPFlag(d) = 0 then LI(d,k) = 1 and LD(d,k) = 1 for all k  SP and all k  if DPFlag(d) = 1 and NMB ≥ 0 then LI(d,k) = 1 and LD(d,k) = 1 for all k  if DPFlag(d) = 1 and NMB <0 then LI(d,k) = 0 and LD(d,k) = 1 for all k  SP if DPFlag(d) = 1 and NMB ≥ 0 then LI(d,k) = 1 and LD(d,k) = 1 for all k  if DPFlag(d) = 1 and NMB < 0 then LI(d,k) = 0 and LD(d,k) = 1 for all k 
```
```
SN  [MAX(0,DQF(p,d,k)) × LI(d,k) -  MIN(0,DQF(p,d,k)) × LD(d,k)] SN SP SN SN
```
