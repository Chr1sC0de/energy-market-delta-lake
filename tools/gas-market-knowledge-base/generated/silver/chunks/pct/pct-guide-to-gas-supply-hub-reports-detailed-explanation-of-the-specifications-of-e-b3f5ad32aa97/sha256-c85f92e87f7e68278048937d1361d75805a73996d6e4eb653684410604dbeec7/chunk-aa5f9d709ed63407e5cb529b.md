---
{
  "chunk_id": "chunk-aa5f9d709ed63407e5cb529b",
  "chunk_ordinal": 90,
  "chunk_text_sha256": "e4d23288b985edc65c6d0680ded7a04348555904eaa8673452cd9557e97dd39c",
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
              "b": 445.64892578125,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.21498107910156,
              "r": 527.3878173828125,
              "t": 712.3904724121094
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 24
          }
        ],
        "self_ref": "#/tables/40"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-aa5f9d709ed63407e5cb529b.md",
  "heading_path": [
    "'I' and 'D' record specifications - bank guarantees"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-aa5f9d709ed63407e5cb529b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

BANK_GUARANTEE_N O, Data Type = STRING(20). BANK_GUARANTEE_N O, Not Null = True. BANK_GUARANTEE_N O, Primary Key = True. BANK_GUARANTEE_N O, Description = The reference number for the bank guarantee included in the prudential run.. BANK_GUARANTEE_N O, Examples = 123456. EFFECTIVE_FROM_DA TE, Data Type = DATE. EFFECTIVE_FROM_DA TE, Not Null = True. EFFECTIVE_FROM_DA TE, Primary Key = False. EFFECTIVE_FROM_DA TE, Description = The start date of the bank guarantee.. EFFECTIVE_FROM_DA TE, Examples = 2013/03/26 00:00:00. EXPIRY_DATE, Data Type = DATE. EXPIRY_DATE, Not Null = True. EXPIRY_DATE, Primary Key = False. EXPIRY_DATE, Description = Expiry date for the bank guarantee.. EXPIRY_DATE, Examples = 2014/07/26 00:00:00. PRUDENTIAL_EXPIRY_ DATE, Data Type = DATE. PRUDENTIAL_EXPIRY_ DATE, Not Null = True.
