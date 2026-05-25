---
{
  "chunk_id": "chunk-4b722d0d3e11bdaba1505a69",
  "chunk_ordinal": 103,
  "chunk_text_sha256": "e6c4957af070f4467a5ea18115d599d9e75a70fb2d3710a8596f71f230478126",
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
              "b": 485.5251159667969,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.48654174804688,
              "r": 527.2430419921875,
              "t": 712.6752014160156
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/tables/46"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-4b722d0d3e11bdaba1505a69.md",
  "heading_path": [
    "'I' and 'D' record specifications - settlement amounts"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-4b722d0d3e11bdaba1505a69.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

PARTICIPANT_CODE, Data Type = STRING(20). PARTICIPANT_CODE, Not Null = True. PARTICIPANT_CODE, Primary Key = True. PARTICIPANT_CODE, Description = The participant code used in the ETS for the participant with the outstanding amounts.. PARTICIPANT_CODE, Examples = ES584. BILLING_PERIOD, Data Type = STRING(20). BILLING_PERIOD, Not Null = True. BILLING_PERIOD, Primary Key = True. BILLING_PERIOD, Description = The billing period.. BILLING_PERIOD, Examples = 3013051400. SETTLEMENT_TYPE, Data Type = STRING(20). SETTLEMENT_TYPE, Not Null = True. SETTLEMENT_TYPE, Primary Key = False. SETTLEMENT_TYPE, Description = The run type of the settlement run (i.e. final, revision, etc.). SETTLEMENT_TYPE, Examples = Revision. SETTLEMENT_VERSION _ID, Data Type = INTEGER. SETTLEMENT_VERSION _ID, Not Null = True. SETTLEMENT_VERSION _ID, Primary Key = False. SETTLEMENT_VERSION _ID, Description = The version number of the settlement run used in this billing period.. SETTLEMENT_VERSION _ID, Examples = 58. SETTLEMENT_EXPOSU RE_AMOUNT, Data Type =
