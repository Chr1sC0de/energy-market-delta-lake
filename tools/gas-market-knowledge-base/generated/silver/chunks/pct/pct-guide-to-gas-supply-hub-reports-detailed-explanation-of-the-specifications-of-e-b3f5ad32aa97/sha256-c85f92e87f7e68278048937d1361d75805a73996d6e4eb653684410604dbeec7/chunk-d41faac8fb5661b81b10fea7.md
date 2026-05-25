---
{
  "chunk_id": "chunk-d41faac8fb5661b81b10fea7",
  "chunk_ordinal": 236,
  "chunk_text_sha256": "fdd9fdbc8eceb9c8a62f016889ad8dc5b0c91f17626526363eb3fb9139c3a67b",
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
              "b": 340.52191162109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 83.91839599609375,
              "r": 527.4170532226562,
              "t": 712.5312576293945
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/tables/111"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md",
    "source_manifest_line_number": 21,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/pipeline-capacity-trading-pct/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/gas_supply_hubs/market_operations/guide-to-gas-supply-hub-reports.pdf?rev=1287f696e327403989f6b9043589beb2&sc_lang=en"
  },
  "content_sha256": "c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7",
  "corpus": "pct",
  "document_family": "pct__guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-each-of-the-reports-produced-for-the-gas-supply-hub-exchange",
  "document_family_id": "pct__guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-each-of-the-reports-produced-for-the-gas-supply-hub-exchange",
  "document_identity": "pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7",
  "document_title": "##### Guide to Gas Supply Hub reports Detailed explanation of the specifications of each of the reports produced for the Gas Supply Hub exchange.",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-d41faac8fb5661b81b10fea7.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-d41faac8fb5661b81b10fea7.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

DELIVERY_POINT, Data Type = STRING(20). DELIVERY_POINT, Not Null = False. DELIVERY_POINT, Primary Key = False. DELIVERY_POINT, Description = Delivery point/s and associated quantities for netted products are determined as part of the participant location netting process. OR NULL if the participant has a zero net position. For non-netted products, the delivery point is reported as per the original executed trade.. DELIVERY_POINT, Examples = Run 1. DELIVERY_TYPE_ALER T, Data Type = STRING(20). DELIVERY_TYPE_ALER T, Not Null = False. DELIVERY_TYPE_ALER T, Primary Key = False. DELIVERY_TYPE_ALER T, Description = This field is empty if the transaction is an output of the delivery netting module. If the transaction is an original executed trade ( for non-netted products or due to a system failure), this field shows 'Non- netted Delivery'.. DELIVERY_TYPE_ALER T, Examples = Non-netted Delivery. ETS_TRADE_ID, Data Type = STRING(20). ETS_TRADE_ID, Not Null = False. ETS_TRADE_ID, Primary Key = False.
