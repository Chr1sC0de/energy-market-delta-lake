---
{
  "chunk_id": "chunk-46bbf2e08f1a8fe5dec3a72f",
  "chunk_ordinal": 108,
  "chunk_text_sha256": "4555f1ae1a9197804efcf400da18ad683c46d8aa8444fe7e53b8aba8223e9237",
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
              "b": 68.98419189453125,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.01591491699219,
              "r": 527.37744140625,
              "t": 310.406982421875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/tables/48"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-46bbf2e08f1a8fe5dec3a72f.md",
  "heading_path": [
    "'I' and 'D' record specifications - trade forward exposure"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-46bbf2e08f1a8fe5dec3a72f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

PRUDENTIAL_DATETIM E, Not Null = True. PRUDENTIAL_DATETIM E, Primary Key = True. PRUDENTIAL_DATETIM E, Description = The date and time of the prudential run.. PRUDENTIAL_DATETIM E, Examples = 2013/04/02 08:15:00. GAS_DATE, Data Type = DATE. GAS_DATE, Not Null = False. GAS_DATE, Primary Key = True. GAS_DATE, Description = The gas day. Disregard the time component as this is not applicable.. GAS_DATE, Examples = 2013/04/13 00:00:00. PRODUCT_LOCATION, Data Type = STRING(80). PRODUCT_LOCATION, Not Null = False. PRODUCT_LOCATION, Primary Key = False. PRODUCT_LOCATION, Description = The product location for the GSH market.. PRODUCT_LOCATION, Examples = WAL. TRADES_FORWARD_E XP_AMT_NET_GST, Data Type = NUMBER. TRADES_FORWARD_E XP_AMT_NET_GST, Not Null = False. TRADES_FORWARD_E XP_AMT_NET_GST, Primary Key = False.
