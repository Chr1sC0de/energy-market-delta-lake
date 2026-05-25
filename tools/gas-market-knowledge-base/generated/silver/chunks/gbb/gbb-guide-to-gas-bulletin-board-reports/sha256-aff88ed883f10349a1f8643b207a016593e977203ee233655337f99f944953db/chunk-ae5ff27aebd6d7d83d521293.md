---
{
  "chunk_id": "chunk-ae5ff27aebd6d7d83d521293",
  "chunk_ordinal": 291,
  "chunk_text_sha256": "61441619efaa12c57cfc0a0d87bc50e0b17a3aa89f00d55804153908dd3f0d59",
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
              "b": 253.25592041015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.69641876220703,
              "r": 542.1180419921875,
              "t": 748.0783615112305
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 65
          }
        ],
        "self_ref": "#/tables/94"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-ae5ff27aebd6d7d83d521293.md",
  "heading_path": [
    "4.32.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-ae5ff27aebd6d7d83d521293.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

ReceiptLocationName, Description = the DeliveryLocationId indicates the capacity direction and location The Connection Point name associated. ReceiptLocationName, Data type = Varchar(200). ReceiptLocationName, Example = Marsden Delivery Stream. DeliveryLocationId, Description = The Connection Point Id that best represents the delivery location associated with a pipeline's nameplate capacity flow direction. The ReceiptLocationId in conjunction with the DeliveryLocationId indicates the capacity direction and location. DeliveryLocationId, Data type = int. DeliveryLocationId, Example = 1202062. DeliveryLocationName, Description = The Connection Point name associated with the DeliveryLocationId. DeliveryLocationName, Data type = Varchar(200). DeliveryLocationName, Example = Dubbo Delivery Stream. Description, Description = Describes the calculation that is being performed in each row of the report. Description, Data type = Varchar(100). Description, Example = Capacity Available. ForecastMethod, Description = Describes the calculation that is being performed for each BB pipeline where the Description is Forecast Flow. ForecastMethod, Data type = Varchar(100). ForecastMethod, Example = Sum of Delivery Points.
