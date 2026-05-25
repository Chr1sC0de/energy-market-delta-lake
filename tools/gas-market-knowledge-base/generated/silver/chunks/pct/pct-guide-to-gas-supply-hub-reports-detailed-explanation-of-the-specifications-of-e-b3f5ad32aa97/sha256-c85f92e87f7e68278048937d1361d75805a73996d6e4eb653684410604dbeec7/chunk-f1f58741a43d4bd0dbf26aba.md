---
{
  "chunk_id": "chunk-f1f58741a43d4bd0dbf26aba",
  "chunk_ordinal": 212,
  "chunk_text_sha256": "4e92d1d91501ff8b3960d758ac7afaa604af3ac99491a511da11cfdea6f2560e",
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
              "b": 131.2703857421875,
              "coord_origin": "BOTTOMLEFT",
              "l": 83.86559295654297,
              "r": 527.3649291992188,
              "t": 712.3912200927734
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 45
          }
        ],
        "self_ref": "#/tables/100"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-f1f58741a43d4bd0dbf26aba.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-f1f58741a43d4bd0dbf26aba.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

PARTICIPANT_ID, Data Type = STRING(20). PARTICIPANT_ID, Not Null = True. PARTICIPANT_ID, Primary Key = True. PARTICIPANT_ID, Description = The unique identifier of the participant. PARTICIPANT_ID, Examples = 74. PARTICIPANT_CODE, Data Type = STRING(20). PARTICIPANT_CODE, Not Null = True. PARTICIPANT_CODE, Primary Key = False. PARTICIPANT_CODE, Description = The participant code used in the Exchange Trading System (ETS). PARTICIPANT_CODE, Examples = ES584. ORGANISATION_NA ME, Data Type = STRING(80). ORGANISATION_NA ME, Not Null = True. ORGANISATION_NA ME, Primary Key = False. ORGANISATION_NA ME, Description =  Name of the organisation who has the ABN. ORGANISATION_NA ME, Examples = AGL. ORGANISATION_CO DE, Data Type = STRING(20). ORGANISATION_CO DE, Not Null = True. ORGANISATION_CO DE, Primary Key = False. ORGANISATION_CO DE, Description = Unique code of the organisation. ORGANISATION_CO DE, Examples = AG256. TRADING_NAME, Data Type = STRING(80). TRADING_NAME, Not Null = True. TRADING_NAME,
