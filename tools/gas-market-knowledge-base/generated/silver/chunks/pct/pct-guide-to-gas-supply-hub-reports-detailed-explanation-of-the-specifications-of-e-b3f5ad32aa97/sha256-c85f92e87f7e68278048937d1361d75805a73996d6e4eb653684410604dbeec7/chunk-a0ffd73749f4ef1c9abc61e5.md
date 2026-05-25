---
{
  "chunk_id": "chunk-a0ffd73749f4ef1c9abc61e5",
  "chunk_ordinal": 80,
  "chunk_text_sha256": "2e183d2281cf0b9094a79d27c84271fd55b85411715e1f3f19105d17184ea085",
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
              "b": 57.76422119140625,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.01564025878906,
              "r": 527.4012451171875,
              "t": 712.5113372802734
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 21
          }
        ],
        "self_ref": "#/tables/35"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-a0ffd73749f4ef1c9abc61e5.md",
  "heading_path": [
    "'I' and 'D' record specifications - estimated market exposure"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-a0ffd73749f4ef1c9abc61e5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

False. EARLY_PAYMENTS, Primary Key = False. EARLY_PAYMENTS, Description = The sum of all applicable early payment amounts for the organisation.. EARLY_PAYMENTS, Examples = 23489. OUTSTANDING_AMO UNT, Data Type = NUMBER. OUTSTANDING_AMO UNT, Not Null = False. OUTSTANDING_AMO UNT, Primary Key = False. OUTSTANDING_AMO UNT, Description = The total outstanding amounts for the organisation. The organisation's outstanding amount equal to the settlement exposure amount, plus reallocation amounts for gas days less than prudential run date where the reallocation amounts were not included in settlement run, minus security deposits minus early payments.. OUTSTANDING_AMO UNT, Examples = 1338000. REALLOC_ADJ_AMT_ TO_OUTSTANDING, Data Type = NUMBER. REALLOC_ADJ_AMT_ TO_OUTSTANDING, Not Null = False. REALLOC_ADJ_AMT_ TO_OUTSTANDING, Primary Key = False. REALLOC_ADJ_AMT_ TO_OUTSTANDING, Description = The total reallocations amounts used as adjustment to outstandings in the prudential run, this include all reallocations
