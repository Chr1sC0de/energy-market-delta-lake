---
{
  "chunk_id": "chunk-d4fd0af2ac666992b886f6a9",
  "chunk_ordinal": 222,
  "chunk_text_sha256": "aada38d0eeea37c47f448e741136cb058e4996d404feac3c660a6a85964a6769",
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
              "b": 346.5736389160156,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.37217712402344,
              "r": 527.3480834960938,
              "t": 712.5715255737305
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 47
          }
        ],
        "self_ref": "#/tables/104"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-d4fd0af2ac666992b886f6a9.md",
  "heading_path": [
    "'I' and 'D' record specifications - reallocation"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-d4fd0af2ac666992b886f6a9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

CREDIT_PARTICIPANT _REFERENCE, Data Type = STRING(80). CREDIT_PARTICIPANT _REFERENCE, Not Null = False. CREDIT_PARTICIPANT _REFERENCE, Primary Key = False. CREDIT_PARTICIPANT _REFERENCE, Description = The reference for the reallocation for the participant on the credit side of the reallocation.. CREDIT_PARTICIPANT _REFERENCE, Examples = Auth AB. START_DATE, Data Type = DATE. START_DATE, Not Null = True. START_DATE, Primary Key = False. START_DATE, Description = The date the reallocation comes into effect. Disregard the time component as this is not applicable.. START_DATE, Examples = 2013/04/22 00:00:00. END_DATE, Data Type = DATE. END_DATE, Not Null = True. END_DATE, Primary Key = False. END_DATE, Description = The date the reallocation ends. Disregard the time component as this is not applicable.. END_DATE, Examples = 2013/04/28 00:00:00. AGREEMENT_TYPE, Data Type = STRING(80). AGREEMENT_TYPE, Not Null = True. AGREEMENT_TYPE, Primary Key = False. AGREEMENT_TYPE, Description = The type of
