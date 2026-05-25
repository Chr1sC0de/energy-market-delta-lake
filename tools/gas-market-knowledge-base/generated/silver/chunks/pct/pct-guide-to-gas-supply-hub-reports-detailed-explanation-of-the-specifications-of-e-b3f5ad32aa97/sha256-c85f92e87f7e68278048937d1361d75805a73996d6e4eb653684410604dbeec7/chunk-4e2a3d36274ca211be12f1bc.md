---
{
  "chunk_id": "chunk-4e2a3d36274ca211be12f1bc",
  "chunk_ordinal": 115,
  "chunk_text_sha256": "c5d57b692389fbf8c8b388a076d6303fdb4405a5626135d29fbced1da8fbcf5e",
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
              "b": 72.70074462890625,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.3189926147461,
              "r": 527.3836059570312,
              "t": 186.966064453125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/tables/51"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-4e2a3d36274ca211be12f1bc.md",
  "heading_path": [
    "'I' and 'D' record specifications - auction forward exposure"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-4e2a3d36274ca211be12f1bc.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

MARKET_ID, Data Type = STRING(20) True. MARKET_ID, Not Null = False. MARKET_ID, Primary Key = . MARKET_ID, Description = Unique Market ID. MARKET_ID, Examples = GSH. ORGANISATION_CO DE, Data Type = STRING(20). ORGANISATION_CO DE, Not Null = True. ORGANISATION_CO DE, Primary Key = True. ORGANISATION_CO DE, Description = The unique code for the organisation.. ORGANISATION_CO DE, Examples = AG256. ORGANISATION_NA STRING(80), Data Type = . ORGANISATION_NA STRING(80), Not Null = True. ORGANISATION_NA STRING(80), Primary Key = False. ORGANISATION_NA STRING(80), Description = The name of the organisation.. ORGANISATION_NA STRING(80), Examples = AGL. PRUDENTIAL_RUN_ID, Data Type = INTEGER. PRUDENTIAL_RUN_ID, Not Null = True. PRUDENTIAL_RUN_ID, Primary Key = True. PRUDENTIAL_RUN_ID, Description = The run number of the prudential run.. PRUDENTIAL_RUN_ID, Examples = 89
