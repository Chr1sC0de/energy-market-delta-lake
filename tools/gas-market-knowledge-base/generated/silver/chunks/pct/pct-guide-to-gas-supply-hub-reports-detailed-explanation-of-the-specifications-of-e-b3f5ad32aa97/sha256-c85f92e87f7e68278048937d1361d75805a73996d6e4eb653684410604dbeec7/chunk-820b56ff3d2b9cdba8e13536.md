---
{
  "chunk_id": "chunk-820b56ff3d2b9cdba8e13536",
  "chunk_ordinal": 132,
  "chunk_text_sha256": "53d0c613d8c7d6017c459ccf822ca2d246197d68eb356acd47b570d13aa4c9aa",
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-820b56ff3d2b9cdba8e13536.md",
  "heading_path": [
    "'I' and 'D' record specifications - settlement run"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-820b56ff3d2b9cdba8e13536.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

'FINAL_PENDING' or 'REVISION_PENDING' respectively.. SETTLEMENT_RUN_TYP E, Examples = Final. START_GAS_DATE, Data Type = DATE. START_GAS_DATE, Not Null = True. START_GAS_DATE, Primary Key = False. START_GAS_DATE, Description = The first gas date of the period when settlement is run. Disregard the time component as this is not applicable.. START_GAS_DATE, Examples = 2013/07/04 00:00:00. END_GAS_DATE, Data Type = DATE. END_GAS_DATE, Not Null = True. END_GAS_DATE, Primary Key = False. END_GAS_DATE, Description = The last gas date of the period when settlement is run. Disregard the time component as this is not applicable.. END_GAS_DATE, Examples = 2013/08/04 00:00:00. LASTCHANGED, Data Type = DATE. LASTCHANGED, Not Null = True. LASTCHANGED, Primary Key = False. LASTCHANGED, Description = The date & time the report was generated.. LASTCHANGED, Examples = 2013/07/04 09:30:58
