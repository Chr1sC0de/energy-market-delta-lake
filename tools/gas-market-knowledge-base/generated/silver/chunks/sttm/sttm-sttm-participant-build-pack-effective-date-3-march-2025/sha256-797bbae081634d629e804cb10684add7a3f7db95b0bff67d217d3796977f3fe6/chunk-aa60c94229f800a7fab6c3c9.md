---
{
  "chunk_id": "chunk-aa60c94229f800a7fab6c3c9",
  "chunk_ordinal": 95,
  "chunk_text_sha256": "ba708e7c93f2c680cf69056c4ffc99be1a35428158683e387f8d69de09c9348f",
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
              "b": 318.2993873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 498.7675999999997,
              "t": 356.1408629101563
            },
            "charspan": [
              0,
              208
            ],
            "page_no": 24
          }
        ],
        "self_ref": "#/texts/406"
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
              "b": 297.779387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 440.44899999999996,
              "t": 306.58086291015627
            },
            "charspan": [
              0,
              77
            ],
            "page_no": 24
          }
        ],
        "self_ref": "#/texts/407"
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
              "b": 235.90179553744758,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 371.32899999999995,
              "t": 286.0608629101563
            },
            "charspan": [
              0,
              130
            ],
            "page_no": 24
          }
        ],
        "self_ref": "#/texts/408"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6/chunk-aa60c94229f800a7fab6c3c9.md",
  "heading_path": [
    "4.1.5. Treatment of literals"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6/chunk-aa60c94229f800a7fab6c3c9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-effective-date-3-march-2025/sha256-797bbae081634d629e804cb10684add7a3f7db95b0bff67d217d3796977f3fe6.md"
}
---

The CSV import application will be able to parse literals irrespective of whether they are surrounded by double-quotes, single-quotes, or not. Commas may be used in the literal if surrounded by double quotes.
A CSV parser will be able to parse and interpret the following CSV file rows:
123, ' This is a sample field, This is another sample field ' ,456 123,'This is a sample field',456 123,This is a sample field,456
