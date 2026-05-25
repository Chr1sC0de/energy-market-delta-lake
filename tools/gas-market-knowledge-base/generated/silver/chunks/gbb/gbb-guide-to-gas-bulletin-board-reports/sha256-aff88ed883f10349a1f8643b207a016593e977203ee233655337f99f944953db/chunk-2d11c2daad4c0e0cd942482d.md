---
{
  "chunk_id": "chunk-2d11c2daad4c0e0cd942482d",
  "chunk_ordinal": 218,
  "chunk_text_sha256": "b339902bb354615960b06f40b087d65d747c1e40b678111bb0481ff56511359c",
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
              "b": 441.90093994140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.546119689941406,
              "r": 541.8241577148438,
              "t": 579.6331481933594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/tables/61"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-2d11c2daad4c0e0cd942482d.md",
  "heading_path": [
    "4.17.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-2d11c2daad4c0e0cd942482d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

FieldName, Description = The name of the Field in which the Field Interest is located. FieldName, Data type = Varchar(100). FieldName, Examples = . FieldInterestId, Description = A unique AEMO defined Field Interest Identifier. FieldInterestId, Data type = Int. FieldInterestId, Examples = 123456. CompanyId, Description = The company ID of the responsible participant. CompanyId, Data type = Int. CompanyId, Examples = 13. CompanyName, Description = The company name of the responsible participant. CompanyName, Data type = Varchar(50). CompanyName, Examples = Bolder Mining Company. GroupMembers, Description = The name of the group member. GroupMembers, Data type = Varchar(50). GroupMembers, Examples = . PercentageShare, Description = The BB field interest (as a percentage) of each member of the field owner group. PercentageShare, Data type = Varchar. PercentageShare, Examples = 32%. EffectiveDate, Description = The date on which the record takes effect. EffectiveDate, Data type = Datetime. EffectiveDate, Examples =
