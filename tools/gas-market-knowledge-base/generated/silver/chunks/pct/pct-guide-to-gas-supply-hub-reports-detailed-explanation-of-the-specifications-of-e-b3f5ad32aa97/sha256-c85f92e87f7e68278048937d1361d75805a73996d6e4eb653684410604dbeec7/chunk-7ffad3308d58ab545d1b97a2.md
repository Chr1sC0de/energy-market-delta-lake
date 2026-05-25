---
{
  "chunk_id": "chunk-7ffad3308d58ab545d1b97a2",
  "chunk_ordinal": 171,
  "chunk_text_sha256": "3d9e730e624662285e4cf123188786f82f87d296e62f499240c398e81a823617",
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
              "b": 61.0552978515625,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.20372772216797,
              "r": 527.291259765625,
              "t": 389.1937255859375
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/tables/79"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-7ffad3308d58ab545d1b97a2.md",
  "heading_path": [
    "'I' and 'D' record specifications - executed trades"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-7ffad3308d58ab545d1b97a2.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

trade was executed. Disregard the time component as this is not applicable.. GAS_DATE, Examples = 2013/07/04 00:00:00. TRADE_ID, Data Type = STRING(20). TRADE_ID, Not Null = True. TRADE_ID, Primary Key = True. TRADE_ID, Description = The unique identifier for the executed trade included in the settlement run. This field can be cross referenced with the TRADE_ID field in the Trade Execution report.. TRADE_ID, Examples = 44. TRADE_SIDE, Data Type = STRING(20). TRADE_SIDE, Not Null = True. TRADE_SIDE, Primary Key = False. TRADE_SIDE, Description = This field specified whether the participant was the buyer or the seller in the trade.. TRADE_SIDE, Examples = Buyer. TRADE_QUANTITY, Data Type = NUMBER. TRADE_QUANTITY, Not Null = True. TRADE_QUANTITY, Primary Key = False. TRADE_QUANTITY, Description = The quantity of the executed trade.. TRADE_QUANTITY, Examples = 78922. TRADE_PRICE, Data Type = NUMBER. TRADE_PRICE, Not Null = True. TRADE_PRICE, Primary Key = False. TRADE_PRICE, Description = The
