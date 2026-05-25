---
{
  "chunk_id": "chunk-6245ec490dea41beaf2734ff",
  "chunk_ordinal": 167,
  "chunk_text_sha256": "bfd533495ef9294092a686641210f58417545b50d23f4f31154fd0972d270f69",
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
              "b": 564.318115234375,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.4048080444336,
              "r": 527.233154296875,
              "t": 712.5884628295898
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/tables/77"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-6245ec490dea41beaf2734ff.md",
  "heading_path": [
    "'I' and 'D' record specifications - ad hoc"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-6245ec490dea41beaf2734ff.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

TYPE, Data Type = STRING(20). TYPE, Not Null = True. TYPE, Primary Key = False. TYPE, Description = Type of the ad hoc amount whether it is a charge or a payment.. TYPE, Examples = Payment. AMOUNT, Data Type = NUMBER. AMOUNT, Not Null = True. AMOUNT, Primary Key = False. AMOUNT, Description = Total amount of ad hoc charge or payment for the gas date excluding GST.. AMOUNT, Examples = -9876.88. GST_AMOUNT, Data Type = NUMBER. GST_AMOUNT, Not Null = True. GST_AMOUNT, Primary Key = False. GST_AMOUNT, Description = Total amount of GST on the ad hoc payment or charge for the gas date.. GST_AMOUNT, Examples = -67.99. ADHOC_DESCRIPTIO N, Data Type = STRING(255). ADHOC_DESCRIPTIO N, Not Null = False. ADHOC_DESCRIPTIO N, Primary Key = False. ADHOC_DESCRIPTIO N, Description = The description of the ad hoc payment.. ADHOC_DESCRIPTIO N, Examples =
