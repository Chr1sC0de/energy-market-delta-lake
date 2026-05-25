---
{
  "chunk_id": "chunk-e17e8f7c364f80f05fdd4a67",
  "chunk_ordinal": 50,
  "chunk_text_sha256": "9c4d1240799ef5bbd5d023e9d41ba4eea450eae6e0d7c1cd2e45543900be7c24",
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
              "b": 58.361083984375,
              "coord_origin": "BOTTOMLEFT",
              "l": 83.80990600585938,
              "r": 527.4121704101562,
              "t": 712.5680541992188
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 14
          }
        ],
        "self_ref": "#/tables/18"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-e17e8f7c364f80f05fdd4a67.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-e17e8f7c364f80f05fdd4a67.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

Point specified by the buyer or seller in an order submission for capacity products.. RECEIPT_POINT, Examples = Run2. ORDER_ID, Data Type = STRING(20). ORDER_ID, Not Null = False. ORDER_ID, Primary Key = False. ORDER_ID, Description = The ID of the order used in the trade from the buyer or the seller side depending on the participant getting the report. This field is null if the TRADE_TYPE is off-market or rarely if the network goes down. This field is also null where the participant uses the 'Deal Order' function to create a trade in the Trayport ETS front-end.. ORDER_ID, Examples = 55. BUYER_USER_NAME, Data Type = STRING(100). BUYER_USER_NAME, Not Null = False. BUYER_USER_NAME, Primary Key = False. BUYER_USER_NAME, Description = Name of the buyer's account that made submission to the exchange.. BUYER_USER_NAME, Examples = abc_trader. SELLER_USER_NAME, Data Type = STRING(100). SELLER_USER_NAME, Not Null = False. SELLER_USER_NAME, Primary Key = False.
