---
{
  "chunk_id": "chunk-04d049b54cb2d7b3d86aff9d",
  "chunk_ordinal": 248,
  "chunk_text_sha256": "c7a570f321cdaeaca48aaed7ec0943ed88d98c34e081a766c9cf4b98f931f675",
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
              "b": 440.504150390625,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.29998779296875,
              "r": 527.2734985351562,
              "t": 712.6043167114258
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 53
          }
        ],
        "self_ref": "#/tables/119"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-04d049b54cb2d7b3d86aff9d.md",
  "heading_path": [
    "Delivery netting preferences"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-04d049b54cb2d7b3d86aff9d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

CHOSEN_POSITION, Data Type = STRING(20). CHOSEN_POSITION, Not Null = False. CHOSEN_POSITION, Primary Key = False. CHOSEN_POSITION, Description = Which type of position is used. Valid values are  NET  BUY/SELL. CHOSEN_POSITION, Examples = NET. USE_TRANSACTIONS, Data Type = STRING(1). USE_TRANSACTIONS, Not Null = False. USE_TRANSACTIONS, Primary Key = False. USE_TRANSACTIONS, Description = Whether original delivery points specified in trades will be used.  Y  N. USE_TRANSACTIONS, Examples = Y. USE_GROUPS, Data Type = STRING(1). USE_GROUPS, Not Null = False. USE_GROUPS, Primary Key = False. USE_GROUPS, Description = Whether original delivery points specified in trades will be used.  Y  N. USE_GROUPS, Examples = N. LAST_UPDATED, Data Type = DATE. LAST_UPDATED, Not Null = True. LAST_UPDATED, Primary Key = False. LAST_UPDATED, Description = The date & time the preference was updated. LAST_UPDATED, Examples = 2016/07/21 13:20:21. LAST_UPDATED_BY, Data Type = STRING(20). LAST_UPDATED_BY, Not Null
