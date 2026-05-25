---
{
  "chunk_id": "chunk-40194ed82fb61ff2586ae1eb",
  "chunk_ordinal": 233,
  "chunk_text_sha256": "4c5fc3c8149ad3cdc1237f2984e7cb606eed34b851f869488150a3d4e6834766",
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
              "b": 159.1407470703125,
              "coord_origin": "BOTTOMLEFT",
              "l": 83.9779052734375,
              "r": 527.54150390625,
              "t": 712.2427520751953
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 49
          }
        ],
        "self_ref": "#/tables/110"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-40194ed82fb61ff2586ae1eb.md",
  "heading_path": [
    "'I' and 'D' record specifications"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-40194ed82fb61ff2586ae1eb.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

BUYER_PARTICIPANT_ CODE, Data Type = STRING(20). BUYER_PARTICIPANT_ CODE, Not Null = True. BUYER_PARTICIPANT_ CODE, Primary Key = False. BUYER_PARTICIPANT_ CODE, Description = The unique identifier for the participant on buy side of the trade that has an obligation to receipt gas OR The unique code for the participant with net zero position.. BUYER_PARTICIPANT_ CODE, Examples = 5. BUYER_PARTICIPANT_ NAME, Data Type = STRING(80). BUYER_PARTICIPANT_ NAME, Not Null = True. BUYER_PARTICIPANT_ NAME, Primary Key = False. BUYER_PARTICIPANT_ NAME, Description = The name for the participant on buy side of the trade that has an obligation to receipt gas OR The name of the participant with net zero position.. BUYER_PARTICIPANT_ NAME, Examples = AGL. SELLER_PARTICIPANT_ CODE, Data Type = STRING(20). SELLER_PARTICIPANT_ CODE, Not Null = True. SELLER_PARTICIPANT_ CODE, Primary Key = False. SELLER_PARTICIPANT_ CODE, Description = The unique identifier for the participant on seller side of the trade that has an obligation to deliver gas OR The unique code for the participant with net zero position.. SELLER_PARTICIPANT_
