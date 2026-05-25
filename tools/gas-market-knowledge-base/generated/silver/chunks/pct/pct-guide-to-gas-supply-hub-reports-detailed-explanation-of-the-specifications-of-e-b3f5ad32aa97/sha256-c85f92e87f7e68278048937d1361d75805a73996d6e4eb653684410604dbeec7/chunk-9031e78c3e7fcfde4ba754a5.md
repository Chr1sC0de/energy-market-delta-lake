---
{
  "chunk_id": "chunk-9031e78c3e7fcfde4ba754a5",
  "chunk_ordinal": 173,
  "chunk_text_sha256": "496a619eea921aa5ef589dacbe7049fedb3be1f5922937b5ba5c18c63aff03b2",
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
        "label": "text",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 684.1644129251622,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.60000225,
              "r": 318.65655716709676,
              "t": 692.22129375
            },
            "charspan": [
              0,
              58
            ],
            "page_no": 38
          }
        ],
        "self_ref": "#/texts/308"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/24"
        },
        "prov": [
          {
            "bbox": {
              "b": 667.0044099251622,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.60000225,
              "r": 371.05838850104334,
              "t": 675.06129075
            },
            "charspan": [
              0,
              65
            ],
            "page_no": 38
          }
        ],
        "self_ref": "#/texts/309"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/24"
        },
        "prov": [
          {
            "bbox": {
              "b": 649.7244144251622,
              "coord_origin": "BOTTOMLEFT",
              "l": 84.60000225,
              "r": 244.85511224292338,
              "t": 657.78129525
            },
            "charspan": [
              0,
              36
            ],
            "page_no": 38
          }
        ],
        "self_ref": "#/texts/310"
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
  "generated_path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-9031e78c3e7fcfde4ba754a5.md",
  "heading_path": [
    "Report notes - executed trades"
  ],
  "path": "generated/silver/chunks/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7/chunk-9031e78c3e7fcfde4ba754a5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-guide-to-gas-supply-hub-reports-detailed-explanation-of-the-specifications-of-e-b3f5ad32aa97/sha256-c85f92e87f7e68278048937d1361d75805a73996d6e4eb653684410604dbeec7.md"
}
---

Executed trades records are sorted in the following order:
-  Ascending order of the 'GAS_DATE', then within each 'GAS_DATE',
-  Ascending order of the 'TRADE_ID'.
