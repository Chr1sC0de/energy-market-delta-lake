---
{
  "chunk_id": "chunk-1bf1bcc4b559ac3e00903d1f",
  "chunk_ordinal": 202,
  "chunk_text_sha256": "d4e59b966041c622c748adf3ae15501962a8682a3f6576b60a3b08b8b4c46904",
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
              "b": 149.6574533864598,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.88,
              "r": 259.01888,
              "t": 158.59085802734376
            },
            "charspan": [
              0,
              48
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/texts/420"
      },
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
              "b": 72.1688232421875,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.16648483276367,
              "r": 542.0675048828125,
              "t": 140.76300048828125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 42
          }
        ],
        "self_ref": "#/tables/53"
      },
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
              "b": 677.2442169189453,
              "coord_origin": "BOTTOMLEFT",
              "l": 53.26227569580078,
              "r": 542.0956420898438,
              "t": 746.9520797729492
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/tables/54"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-1bf1bcc4b559ac3e00903d1f.md",
  "heading_path": [
    "4.14.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-1bf1bcc4b559ac3e00903d1f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

The following fields are provided in the report.
TransactionId, Description = Unique shipment identifier. TransactionId, Data type = Varchar(40). TransactionId, Examples = 123456. FacilityId, Description = Unique facility identifier.. FacilityId, Data type = Int. FacilityId, Examples = 123456. FacilityName, Description = Name of the facility. FacilityName, Data type = Varchar(100). FacilityName, Examples = ABC LNG. VolumePJ, Description = Volume of the shipment in PJ. VolumePJ, Data type = Numeric(10,3). VolumePJ, Examples = 2.345
ShipmentDate, Description = For LNG export facility, the departure date. For LNG import facility, the date unloading commences at the LNG import facility. ShipmentDate, Data type = Datetime. ShipmentDate, Examples = 2022-04-20. VersionDateTime, Description = Time a successful submission is accepted by AEMO systems. VersionDateTime, Data type = Datetime. VersionDateTime, Examples = 2022-04-20
