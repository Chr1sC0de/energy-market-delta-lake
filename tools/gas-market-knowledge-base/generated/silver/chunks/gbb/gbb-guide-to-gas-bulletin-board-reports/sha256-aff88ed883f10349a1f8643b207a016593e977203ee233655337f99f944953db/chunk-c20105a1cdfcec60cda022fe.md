---
{
  "chunk_id": "chunk-c20105a1cdfcec60cda022fe",
  "chunk_ordinal": 149,
  "chunk_text_sha256": "4bf50d36994ec7828859a8b56fff37d6af5724833aa7316c46f52e3a9e9666bc",
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
              "b": 403.5061950683594,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.74073028564453,
              "r": 541.946044921875,
              "t": 701.5067596435547
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/tables/34"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-c20105a1cdfcec60cda022fe.md",
  "heading_path": [
    "4.7.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-c20105a1cdfcec60cda022fe.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

GasDate, Description = Date of gas day.. GasDate, Data type = Datetime. GasDate, Examples = 2018-09-23. FacilityName, Description = The name of the BB facility.. FacilityName, Data type = varchar (100). FacilityName, Examples = Berwyndale to Wallumbilla Pipeline. FacilityType, Description = Facility type associated with the Facility Id.. FacilityType, Data type = varchar(40). FacilityType, Examples = PIPE; PROD; STOR; COMPRESSOR; LNGIMPORT. State, Description = Name of the state.. State, Data type = char(3). State, Examples = NSW. LocationName, Description = Name of the location.. LocationName, Data type = varchar (100). LocationName, Examples = Sydney (SYD). Demand, Description = Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.. Demand, Data type = number(18,3). Demand, Examples = 32.232 25.2 (if Actual Delivery Quantity is 25.200). Supply, Description = Usage type expressed in TJ. Three
