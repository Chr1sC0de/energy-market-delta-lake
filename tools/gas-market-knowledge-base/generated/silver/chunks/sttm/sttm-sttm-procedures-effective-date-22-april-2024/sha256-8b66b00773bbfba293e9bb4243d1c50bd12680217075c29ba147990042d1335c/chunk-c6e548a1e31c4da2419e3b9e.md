---
{
  "chunk_id": "chunk-c6e548a1e31c4da2419e3b9e",
  "chunk_ordinal": 274,
  "chunk_text_sha256": "c2e50be9bd4ce6a2eab5ddb912fe696f18f5d065ebec2364540893d112a2208b",
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
              "b": 392.50884238062474,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 529.0809999999999,
              "t": 491.90198291015633
            },
            "charspan": [
              0,
              773
            ],
            "page_no": 73
          }
        ],
        "self_ref": "#/texts/1221"
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
              "b": 347.2488423806247,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 525.7610000000004,
              "t": 381.3819829101563
            },
            "charspan": [
              0,
              238
            ],
            "page_no": 73
          }
        ],
        "self_ref": "#/texts/1222"
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
              "b": 315.0888423806248,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 499.8470000000008,
              "t": 336.1219829101563
            },
            "charspan": [
              0,
              152
            ],
            "page_no": 73
          }
        ],
        "self_ref": "#/texts/1223"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-c6e548a1e31c4da2419e3b9e.md",
  "heading_path": [
    "10.5.3. Allocation to steps -Percentage method"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c/chunk-c6e548a1e31c4da2419e3b9e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-22-april-2024/sha256-8b66b00773bbfba293e9bb4243d1c50bd12680217075c29ba147990042d1335c.md"
}
---

Note : This equation states that if there is no variation then there is no variation charge .  However, if there is a variation, then we calculate the per GJ cost of the total variation charge .  If this charge rate is greater than the amount by which the maximum market price exceeds the ex ante market price then the raw variation charge rate is capped at the amount by which the maximum price exceeds the ex ante market price .  The final rate is multiplied by the variation quantity.  This approach effectively caps the average charge applied to be no greater than the applicable maximum market price less the ex ante market price .  The maximum price allowed in the ex ante market for gas day d is MAXP(d) (which will either be MPC, or APC if prices are administered).
This ensures that a Trading Participant who traded its MSV quantity at the ex ante market price will never have a variation charge which would bring its total $/GJ payment for that gas to exceed the applicable maximum price in the market.
The absolute value of the hub price is used in defining the raw value so as to ensure that the variation charge is positive valued if HP(d) is negative.
