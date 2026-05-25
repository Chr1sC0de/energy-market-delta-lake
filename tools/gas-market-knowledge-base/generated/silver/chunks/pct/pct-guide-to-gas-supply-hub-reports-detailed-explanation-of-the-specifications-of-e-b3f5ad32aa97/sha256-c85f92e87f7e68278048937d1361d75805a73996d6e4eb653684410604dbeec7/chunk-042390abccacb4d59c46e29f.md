---
{
  "chunk_id": "chunk-042390abccacb4d59c46e29f",
  "chunk_ordinal": 220,
  "chunk_text_sha256": "2f80b0a167b12471c2245b03553c2f33b7808150e7f6537a676b652fbb282a66",
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
              "b": 59.6722412109375,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.2895736694336,
              "r": 527.1549682617188,
              "t": 305.7273254394531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 46
          }
        ],
        "self_ref": "#/tables/103"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-042390abccacb4d59c46e29f.md",
  "heading_path": [
    "'I' and 'D' record specifications - reallocation"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-042390abccacb4d59c46e29f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

MARKET_ID, Data Type = STRING(20). MARKET_ID, Not Null = True. MARKET_ID, Primary Key = False. MARKET_ID, Description = Unique Market ID. MARKET_ID, Examples = GSH. REALLOCATION_ID, Data Type = STRING(80). REALLOCATION_ID, Not Null = True. REALLOCATION_ID, Primary Key = True. REALLOCATION_ID, Description = The unique identifier for the reallocation.. REALLOCATION_ID, Examples = 20130509.RS003. DEBIT_PARTICIPANT_ CODE, Data Type = STRING(20). DEBIT_PARTICIPANT_ CODE, Not Null = True. DEBIT_PARTICIPANT_ CODE, Primary Key = False. DEBIT_PARTICIPANT_ CODE, Description = The participant code for the participant on the debit side of the reallocation.. DEBIT_PARTICIPANT_ CODE, Examples = AG584. DEBIT_PARTICIPANT_ NAME, Data Type = STRING(80). DEBIT_PARTICIPANT_ NAME, Not Null = True. DEBIT_PARTICIPANT_ NAME, Primary Key = False. DEBIT_PARTICIPANT_ NAME, Description = The name for the participant on the
