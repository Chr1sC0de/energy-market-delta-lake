---
{
  "chunk_id": "chunk-e841395a9fa27dba3c0552df",
  "chunk_ordinal": 212,
  "chunk_text_sha256": "cea5723494330b688b6b78d0f6d8b48670a9bd64f17e95fd5fe7368c1aad4b9c",
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
              "b": 144.17620849609375,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.03810501098633,
              "r": 541.9822998046875,
              "t": 579.8537292480469
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/tables/59"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e841395a9fa27dba3c0552df.md",
  "heading_path": [
    "4.16.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e841395a9fa27dba3c0552df.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

FieldInterestId, Description = A unique AEMO defined Field Interest Identifier. FieldInterestId, Data type = Int. FieldInterestId, Examples = 123456. FieldName, Description = The name of the Field in which the Field Interest is located. FieldName, Data type = Varchar(100). FieldName, Examples = . CompanyID, Description = The company ID of the responsible participant. CompanyID, Data type = Int. CompanyID, Examples = 13. CompanyName, Description = The company name of the responsible participant. CompanyName, Data type = Varchar(50). CompanyName, Examples = Bolder Mining Company. Description, Description = Additional information relating to the field. Description, Data type = Varchar(400). Description, Examples = . EffectiveDate, Description = The date on which the record takes effect. EffectiveDate, Data type = Datetime. EffectiveDate, Examples = 2022-06-23. PetroleumTenements, Description = The petroleum tenements which are the subject of the BB field interest. PetroleumTenements, Data type = Varchar(300). PetroleumTenements, Examples = Petroleum Tenement 3A.
