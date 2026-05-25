---
{
  "chunk_id": "chunk-3f3490a8a2ad01c21aa0f11c",
  "chunk_ordinal": 337,
  "chunk_text_sha256": "c1574f5f830f5e8f84f9bb2f2c136739d4f90e9046c8278d0f4c680b1a38605f",
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
              "b": 189.899387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 527.45392,
              "t": 213.22086291015626
            },
            "charspan": [
              0,
              117
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/texts/1565"
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
              "b": 130.46938739080804,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 405.1553200000001,
              "t": 178.50798291015622
            },
            "charspan": [
              0,
              118
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/texts/1566"
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
              "b": 84.99338739080804,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 432.03652000000017,
              "t": 118.51086291015633
            },
            "charspan": [
              0,
              238
            ],
            "page_no": 89
          }
        ],
        "self_ref": "#/texts/1567"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-3f3490a8a2ad01c21aa0f11c.md",
  "heading_path": [
    "10.10.4. Residual surplus and shortfall allocation based on withdrawals"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-3f3490a8a2ad01c21aa0f11c.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

The shortfall/surplus allocation to Trading Participant p based on withdrawals for the hub for the billing period is:
<!-- formula-not-decoded -->
```
WDA(p) = {NMB - p' DVA(p') +  d  p' VarC( p',d)} ×  [  d  BP {  k  SN  cf(k) AQ U (p,d,cf(k)) +  k  SP  cf(k) AQ S (p,d,cf(k)) } / (  p'  d  BP {  k  SN  cf(k) AQ U (p',d,cf(k)) +  k  SP  cf(k) AQ S (p',d,cf(k))  } ) ]
```
