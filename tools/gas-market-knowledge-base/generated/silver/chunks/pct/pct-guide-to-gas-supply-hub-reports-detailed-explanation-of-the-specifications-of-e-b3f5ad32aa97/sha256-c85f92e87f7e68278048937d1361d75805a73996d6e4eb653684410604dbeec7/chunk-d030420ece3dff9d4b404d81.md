---
{
  "chunk_id": "chunk-d030420ece3dff9d4b404d81",
  "chunk_ordinal": 154,
  "chunk_text_sha256": "98ecbd7a170ac5119b49d3b436ce9afde3ab51ae2fd3f50fd245daa758007ebf",
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
              "b": 63.88055419921875,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.10120391845703,
              "r": 527.4136352539062,
              "t": 260.3192138671875
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/tables/69"
      },
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
              "b": 613.4162292480469,
              "coord_origin": "BOTTOMLEFT",
              "l": 83.96212768554688,
              "r": 527.33740234375,
              "t": 712.5595245361328
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/tables/70"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-d030420ece3dff9d4b404d81.md",
  "heading_path": [
    "'I' and 'D' record specifications - delivery variance"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-d030420ece3dff9d4b404d81.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

delivery variance payment or charge. Disregard the time component as this is not applicable.. GAS_DATE, Examples = 2013/07/04 00:00:00. TYPE, Data Type = STRING(20). TYPE, Not Null = True. TYPE, Primary Key = False. TYPE, Description = Type of the delivery variance amount whether it is a charge or a payment.. TYPE, Examples = Payment
AMOUNT NUMBER, Data Type = True. AMOUNT NUMBER, Not Null = False. AMOUNT NUMBER, Primary Key = . AMOUNT NUMBER, Description = Total amount of delivery variance charge or payment for the gas date excluding GST.. AMOUNT NUMBER, Examples = -3456.87. GST_AMOUNT, Data Type = NUMBER. GST_AMOUNT, Not Null = True. GST_AMOUNT, Primary Key = False. GST_AMOUNT, Description = Total amount of GST on the delivery variance payment or charge for the gas date.. GST_AMOUNT, Examples = -78.99
