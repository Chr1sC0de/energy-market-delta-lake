---
{
  "chunk_id": "chunk-9f1db2a9517c4c6e91adabf3",
  "chunk_ordinal": 66,
  "chunk_text_sha256": "40da6b4b643ce73dc76d9ef707cccd9458be69405e46460fc7dd45e06fff5540",
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
              "b": 214.546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.263916015625,
              "r": 527.4817504882812,
              "t": 712.2247924804688
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 18
          }
        ],
        "self_ref": "#/tables/27"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-9f1db2a9517c4c6e91adabf3.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-9f1db2a9517c4c6e91adabf3.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

PRODUCT_LOCATION, Data Type = STRING(80). PRODUCT_LOCATION, Not Null = True. PRODUCT_LOCATION, Primary Key = True. PRODUCT_LOCATION, Description = Product location for the GSH market.. PRODUCT_LOCATION, Examples = WAL, MAP, MSP, WAL Non-Netted, WAL Compression. PRODUCT_TYPE, Data Type = STRING(80). PRODUCT_TYPE, Not Null = True. PRODUCT_TYPE, Primary Key = False. PRODUCT_TYPE, Description = The product delivery period for the GSH market :  Gas - NG Prompt (Balance of day)  Gas - NG DA Days (Day ahead)  Gas - NG Days (Daily)  Gas - NG Weeks (Weekly)  Gas - NG Months (Monthly). PRODUCT_TYPE, Examples = Gas - NG Weeks. FROM_GAS_DATE, Data Type = DATE. FROM_GAS_DATE, Not Null = True. FROM_GAS_DATE, Primary Key = False. FROM_GAS_DATE, Description = The start gas day for the order delivery period. Disregard the time component as this is not applicable.. FROM_GAS_DATE, Examples = 2013/04/22 00:00:00. TO_GAS_DATE, Data Type = DATE.
