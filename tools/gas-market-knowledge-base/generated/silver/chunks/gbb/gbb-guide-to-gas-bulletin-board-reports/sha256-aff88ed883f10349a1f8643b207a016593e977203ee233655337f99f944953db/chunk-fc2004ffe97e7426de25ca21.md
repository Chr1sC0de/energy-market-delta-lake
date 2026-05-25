---
{
  "chunk_id": "chunk-fc2004ffe97e7426de25ca21",
  "chunk_ordinal": 206,
  "chunk_text_sha256": "4a1d3499908689a314f6b9f11a40c00e968343f1bc43dc3f2e5fdf9a3f936028",
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
              "b": 80.20654296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.40975570678711,
              "r": 542.0621948242188,
              "t": 218.45880126953125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/tables/56"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-fc2004ffe97e7426de25ca21.md",
  "heading_path": [
    "4.15.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-fc2004ffe97e7426de25ca21.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

DevFacilityId, Description = A unique AEMO defined Development Facility Identifier. DevFacilityId, Data type = Int. DevFacilityId, Examples = 123456. ProposedName, Description = The name of the Facility development. ProposedName, Data type = Varchar(100). ProposedName, Examples = Austral LNG. EffectiveDate, Description = The effective date of the submission. EffectiveDate, Data type = Datetime. EffectiveDate, Examples = 2022-04-20. FacilityType, Description = The facility development type. FacilityType, Data type = Varchar(40). FacilityType, Examples = LNGExport. MinNameplate, Description = The lower estimate of nameplate rating capacity. MinNameplate, Data type = Numeric(18,3). MinNameplate, Examples = 111.321. MaxNameplate, Description = The upper estimate of nameplate rating capacity. MaxNameplate, Data type = Numeric(18,3). MaxNameplate, Examples = 143.321. Location, Description = The location of the development facility. Location, Data type = Varchar(200). Location, Examples = Sydney
