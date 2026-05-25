---
{
  "chunk_id": "chunk-8bf48f7b6a3f047892eadb15",
  "chunk_ordinal": 73,
  "chunk_text_sha256": "6ad47efa5d88bee8975952c0fdcb9a1ef6254ae7b1fdbd819f720ca68170807c",
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
              "b": 126.9573974609375,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.36885833740234,
              "r": 527.2575073242188,
              "t": 423.466064453125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 19
          }
        ],
        "self_ref": "#/tables/31"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-8bf48f7b6a3f047892eadb15.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-8bf48f7b6a3f047892eadb15.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

GAS_DATE, Data Type = DATE. GAS_DATE, Not Null = True. GAS_DATE, Primary Key = True. GAS_DATE, Description = The gas date when the delivery of trades occurred. Disregard the time component as this is not applicable.. GAS_DATE, Examples = 2013/04/22 00:00:00. PRODUCT_LOCATION, Data Type = STRING(80). PRODUCT_LOCATION, Not Null = True. PRODUCT_LOCATION, Primary Key = True. PRODUCT_LOCATION, Description = Product location for the GSH market.. PRODUCT_LOCATION, Examples = WAL, WAL Compression. VOLUME_WEIGHTED_ AVERAGE_PRICE, Data Type = NUMBER. VOLUME_WEIGHTED_ AVERAGE_PRICE, Not Null = False. VOLUME_WEIGHTED_ AVERAGE_PRICE, Primary Key = False. VOLUME_WEIGHTED_ AVERAGE_PRICE, Description = The volume weighted average price for trades (not including manual trades) delivered in the specified gas day at the specified location in $/GJ. Specified to eight decimal places.. VOLUME_WEIGHTED_ AVERAGE_PRICE, Examples = 2.54346843. TOTAL_QUANTITY, Data Type = NUMBER. TOTAL_QUANTITY, Not Null = False. TOTAL_QUANTITY, Primary Key =
