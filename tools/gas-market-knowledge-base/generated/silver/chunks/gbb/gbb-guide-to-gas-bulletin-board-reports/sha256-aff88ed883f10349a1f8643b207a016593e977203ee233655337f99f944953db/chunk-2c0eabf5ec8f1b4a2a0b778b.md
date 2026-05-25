---
{
  "chunk_id": "chunk-2c0eabf5ec8f1b4a2a0b778b",
  "chunk_ordinal": 109,
  "chunk_text_sha256": "634bbb2f7ab928c21d8053ed15b312660a0f3c0ceb913489c058c533f26bc66e",
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
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 71.421630859375,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.58028793334961,
              "r": 542.331787109375,
              "t": 354.36468505859375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/tables/20"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md",
    "source_manifest_line_number": 14,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/natural_gas_services_bulletin_board/site-content/gbb-documents/guides-and-procedures/guide-to-gas-bulletin-board-reports.pdf?rev=8d79cc57e0fd4faf9f5c92e94b42f86b&sc_lang=en"
  },
  "content_sha256": "aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db",
  "corpus": "gbb",
  "document_family": "gbb__guide-to-gas-bulletin-board-reports",
  "document_family_id": "gbb__guide-to-gas-bulletin-board-reports",
  "document_identity": "gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db",
  "document_title": "##### Guide to Gas Bulletin Board Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-2c0eabf5ec8f1b4a2a0b778b.md",
  "heading_path": [
    "4.2.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-2c0eabf5ec8f1b4a2a0b778b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

facility.. OperatorName, Data type = varchar(50). OperatorName, Example = Jemena Eastern Gas Pipeline (1) Pty Ltd. OperatorId, Description = The facility operator's ID. OperatorId, Data type = bigint. OperatorId, Example = 138. CapacityQuantity, Description = Standing capacity quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.. CapacityQuantity, Data type = number(18,3). CapacityQuantity, Example = 32.232 25.2 (if the value is 25.200). EffectiveDate, Description = Gas day date that corresponding record takes effect. Any time component supplied will be ignored.. EffectiveDate, Data type = datetime. EffectiveDate, Example = 2018-03-23. Description, Description = Reasons or comments directly related to the capacity quantity or the change in quantity provided in relation to a BB facility. Description, Data type = Varchar (255). Description, Example =
