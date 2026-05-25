---
{
  "chunk_id": "chunk-c9f76d9274fea12fc4370be2",
  "chunk_ordinal": 235,
  "chunk_text_sha256": "ebaf61d320ae010203ae072334e9b93feee6d35b604eb1e63da434de9a700f29",
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
              "b": 159.1407470703125,
              "coord_origin": "BOTTOMLEFT",
              "l": 83.9779052734375,
              "r": 527.54150390625,
              "t": 712.2427520751953
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/tables/110"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-c9f76d9274fea12fc4370be2.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-c9f76d9274fea12fc4370be2.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

TO_GAS_DATE, Data Type = DATE. TO_GAS_DATE, Not Null = True. TO_GAS_DATE, Primary Key = False. TO_GAS_DATE, Description = The last gas date of the netting period. Disregard the time component as this is not applicable.. TO_GAS_DATE, Examples = 2013/04/13 00:00:00. PRODUCT_LOCATION, Data Type = STRING(80). PRODUCT_LOCATION, Not Null = True. PRODUCT_LOCATION, Primary Key = False. PRODUCT_LOCATION, Description = The product location, product grouping code for the GSH market. PRODUCT_LOCATION, Examples = WAL. DELIVERY_QUANTITY, Data Type = NUMBER. DELIVERY_QUANTITY, Not Null = True. DELIVERY_QUANTITY, Primary Key = False. DELIVERY_QUANTITY, Description = The quantity of the delivery transaction GJ/day OR Zero if the participant has a zero net position.. DELIVERY_QUANTITY, Examples = 755
