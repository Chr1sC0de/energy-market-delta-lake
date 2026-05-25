---
{
  "chunk_id": "chunk-83b3c10a73a22ec67c822bcb",
  "chunk_ordinal": 131,
  "chunk_text_sha256": "736d1950976e62a6665a6da9f325e32b236e6ae2146ceb983c86878efa7935f0",
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
              "b": 418.3612976074219,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.42841339111328,
              "r": 527.110107421875,
              "t": 712.3721313476562
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 31
          }
        ],
        "self_ref": "#/tables/58"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-83b3c10a73a22ec67c822bcb.md",
  "heading_path": [
    "'I' and 'D' record specifications - settlement run"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-83b3c10a73a22ec67c822bcb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

MARKET_ID, Data Type = STRING(20). MARKET_ID, Not Null = True. MARKET_ID, Primary Key = False. MARKET_ID, Description = Unique Market ID. MARKET_ID, Examples = GSH. SETTLEMENT_RUN_ID, Data Type = INTEGER. SETTLEMENT_RUN_ID, Not Null = True. SETTLEMENT_RUN_ID, Primary Key = True. SETTLEMENT_RUN_ID, Description = The unique identifier for the settlement run.. SETTLEMENT_RUN_ID, Examples = 45. BILLING_PERIOD, Data Type = STRING(20). BILLING_PERIOD, Not Null = False. BILLING_PERIOD, Primary Key = False. BILLING_PERIOD, Description = The billing period for the settlement run.. BILLING_PERIOD, Examples = 2013041200. SETTLEMENT_RUN_TYP E, Data Type = STRING(20). SETTLEMENT_RUN_TYP E, Not Null = True. SETTLEMENT_RUN_TYP E, Primary Key = False. SETTLEMENT_RUN_TYP E, Description = The run type for the settlement, for example final, revision, initial, adjustment. If the final or revision settlement data has not been posted, this value will be
