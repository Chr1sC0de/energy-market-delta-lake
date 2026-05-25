---
{
  "chunk_id": "chunk-0accdbc936b539a66c7ae56a",
  "chunk_ordinal": 116,
  "chunk_text_sha256": "51b2936d0d83182de362a9feb4eecfdd32525c60bc4e9b432300ba084cc34298",
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
              "b": 182.09796142578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.36774826049805,
              "r": 541.9357299804688,
              "t": 368.0336608886719
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 20
          }
        ],
        "self_ref": "#/tables/23"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-0accdbc936b539a66c7ae56a.md",
  "heading_path": [
    "4.3.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-0accdbc936b539a66c7ae56a.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

GasDate, Description = Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.. GasDate, Data type = datetime. GasDate, Example = 2018-09-23. FacilityId, Description = A unique AEMO defined Facility identifier.. FacilityId, Data type = int. FacilityId, Example = 520345. FacilityName, Description = The name of the BB facility.. FacilityName, Data type = varchar(255). FacilityName, Example = Berwyndale to Wallumbilla Pipeline. FacilityType, Description = The type of facility. FacilityType, Data type = Varchar(40). FacilityType, Example = COMPRESSOR, PIPE. Flag, Description = The flags are traffic light colours (Green, Amber, Red) indicating the LCA status for each pipeline. For more information, see the table below.. Flag, Data type = char(5). Flag, Example = RED;AMBER;GREEN. Description, Description = Free text facility use is restricted to a description for reasons or comments directly related to the change in the LCA flag and the times, dates, or duration for which those changes are expected to
