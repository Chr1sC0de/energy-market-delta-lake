---
{
  "chunk_id": "chunk-d5c30814e89dfa6ae448c06b",
  "chunk_ordinal": 74,
  "chunk_text_sha256": "c878d7fe14c25b32e929585ea0922e412e8d82f9b75da15d8e86f83288f735df",
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
              "b": 432.179387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 526.88524,
              "t": 477.2408629101563
            },
            "charspan": [
              0,
              323
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/561"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/35"
        },
        "prov": [
          {
            "bbox": {
              "b": 389.579387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.144,
              "r": 526.8169200000001,
              "t": 422.6208629101563
            },
            "charspan": [
              0,
              210
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/562"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/35"
        },
        "prov": [
          {
            "bbox": {
              "b": 334.979387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.144,
              "r": 516.00808,
              "t": 380.1408629101563
            },
            "charspan": [
              0,
              328
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/563"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/35"
        },
        "prov": [
          {
            "bbox": {
              "b": 292.499387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 75.144,
              "r": 515.0840399999998,
              "t": 325.5408629101563
            },
            "charspan": [
              0,
              230
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/564"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516.md",
    "source_manifest_line_number": 39,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/wa/2025/technical-guide-to-the-wa-gas-retail-market-ver-4-2-clean.pdf?rev=4e21f3036a8a4730b5d65299dd845aa2&sc_lang=en"
  },
  "content_sha256": "59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516",
  "corpus": "retail_gas",
  "document_family": "retail-gas__technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025",
  "document_family_id": "retail-gas__technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025",
  "document_identity": "retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516",
  "document_title": "##### Technical Guide to the WA Gas Retail Market ver (Clean) Effective 7 April 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516/chunk-d5c30814e89dfa6ae448c06b.md",
  "heading_path": [
    "8. BALANCING, ALLOCATION AND RECONCILIATION MANAGEMENT"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516/chunk-d5c30814e89dfa6ae448c06b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516.md"
}
---

AEMO performs the balancing, allocation and reconciliation ('BAR') functions for the WA gas retail market; and calculates the gas injection and withdrawal quantities for each sub-network for each day. The BAR functions are performed in accordance with Chapter 5 of the Procedures, and the calculations are made by the GRMS.
- Balancing: these processes are designed so that the gas injection and withdrawal quantities across each sub-network for each day are always in balance (i.e. total injections equal total withdrawals each day).
- Allocation: means allocating the gas injections into a sub-network for a gas day to the various withdrawals from each of the User's operating in the sub -network. Allocations are undertaken by calculating the User's estimated total withdrawals ('UETW') whic h are reconciled to account for data changes from the past 425 days.
- Reconciliation: these processes are done on a forward basis (i.e. today's errors are fixed the day after tomorrow). Estimations or errors used for today's allocations are fixed over the 28 days commencing the day after tomorrow.
