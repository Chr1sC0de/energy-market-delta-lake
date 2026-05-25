---
{
  "chunk_id": "chunk-78522ece3288a34d05bdda9e",
  "chunk_ordinal": 91,
  "chunk_text_sha256": "d19421379a4c2792e8a481c65ed0d78b022bb98e0a34892a23810f21d5581a2c",
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-78522ece3288a34d05bdda9e.md",
  "heading_path": [
    "'I' and 'D' record specifications - bank guarantees"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-78522ece3288a34d05bdda9e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

PRUDENTIAL_EXPIRY_ DATE, Primary Key = False. PRUDENTIAL_EXPIRY_ DATE, Description = The prudential expiry date of the guarantee.. PRUDENTIAL_EXPIRY_ DATE, Examples = 2014/03/28 00:00:00. AMOUNT, Data Type = NUMBER. AMOUNT, Not Null = True. AMOUNT, Primary Key = False. AMOUNT, Description = The dollar amount of the guarantee applicable to the prudential run.. AMOUNT, Examples = 500000. BANK_GUARANTEE_A LERT, Data Type = STRING(255). BANK_GUARANTEE_A LERT, Not Null = False. BANK_GUARANTEE_A LERT, Primary Key = False. BANK_GUARANTEE_A LERT, Description = The field shows the warning 'Renew Bank Guarantee Warning' if the prudential expiry date of the bank guarantee is within the next 30 days (PRUDENTIAL_EXPIRY_DATE is less than or equal to PRUDENTIAL_DATETIME + 30 days), otherwise it has no value.. BANK_GUARANTEE_A LERT, Examples = Renew Bank Guarantee Warning
