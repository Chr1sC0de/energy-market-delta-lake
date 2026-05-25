---
{
  "chunk_id": "chunk-4320fa4ccce90fa2707aab61",
  "chunk_ordinal": 89,
  "chunk_text_sha256": "5e02f973056a0a53e831ecd6ff65c47fc4ff1adbcc00fdef496f33c026c16da7",
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
              "b": 408.919387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 527.9884000000001,
              "t": 461.28086291015626
            },
            "charspan": [
              0,
              351
            ],
            "page_no": 22
          }
        ],
        "self_ref": "#/texts/382"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6.md",
    "source_manifest_line_number": 42,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-participant-build-pack-v201.pdf?rev=81258e244e9f499dbab23d4eae1d8185&sc_lang=en"
  },
  "content_sha256": "797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6",
  "corpus": "sttm",
  "document_family": "sttm__sttm-participant-build-pack-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-participant-build-pack-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6",
  "document_title": "##### STTM Participant Build Pack Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6/chunk-4320fa4ccce90fa2707aab61.md",
  "heading_path": [
    "3.14. SWEXIE flow control management"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6/chunk-4320fa4ccce90fa2707aab61.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6.md"
}
---

Gateway Service provides the following flow control management functionality. This functionality is a protection mechanism against file overloading of Market Operator's Outbox. This is managed by posting a ' stop.txt ' in the in folder of the STTM Participant. Gateway Service will not process files from any folder that has ' stop.txt ' posted in it.
