---
{
  "chunk_id": "chunk-e0eaec4a4a2be5f33e0b2ce1",
  "chunk_ordinal": 142,
  "chunk_text_sha256": "27b7f56b09a82aba3b9934aa0cb1f4f2e91acc188fe64b5a6b1d739f2402b866",
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
              "b": 201.27520751953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.39088821411133,
              "r": 542.3927001953125,
              "t": 748.0366363525391
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/tables/32"
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
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e0eaec4a4a2be5f33e0b2ce1.md",
  "heading_path": [
    "4.6.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-e0eaec4a4a2be5f33e0b2ce1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

FlowDirection, Example / Allowed values = RECEIPT; DELIVERY; PROCESSED; DELIVERYLNGSTOR; NONE;. CapacityDescription, Description = Free text to describe the meaning of the capacity number provided, including relevant assumptions made in the calculation of the capacity number and any other relevant information. Only provided for BB pipelines or BB compression facilities .. CapacityDescription, Data type = varchar(1000). CapacityDescription, Example / Allowed values = This transmission capacity is the amount of gas that the Culcairn delivery point is able to withdraw from this pipeline facility. ReceiptLocation, Description = The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location. Note : Applicable to BB pipelines only. For other BB facilities , this field is populated with -1.. ReceiptLocation, Data type = Int. ReceiptLocation, Example / Allowed values = 1200001 -1 (for BB facilities other than BB pipelines ). ReceiptLocationName, Description = The name of the receipt location. ReceiptLocationName, Data type = varhar(200). ReceiptLocationName, Example / Allowed values = DDP to APLNG
