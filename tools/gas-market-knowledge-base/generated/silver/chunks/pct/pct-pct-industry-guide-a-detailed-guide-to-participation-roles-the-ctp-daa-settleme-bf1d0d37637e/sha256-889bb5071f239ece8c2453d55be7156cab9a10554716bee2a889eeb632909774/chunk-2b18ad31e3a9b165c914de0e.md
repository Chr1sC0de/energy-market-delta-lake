---
{
  "chunk_id": "chunk-2b18ad31e3a9b165c914de0e",
  "chunk_ordinal": 87,
  "chunk_text_sha256": "ce88bfd6226236c52584c89028487d2eb81993c2c4d47df0291b8b70136c79bf",
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
              "b": 386.58458600972403,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.39999775,
              "r": 531.9137108683556,
              "t": 435.1323156953125
            },
            "charspan": [
              0,
              378
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/339"
      },
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
              "b": 355.024619009724,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.39999775,
              "r": 530.8466668111768,
              "t": 376.9322886953124
            },
            "charspan": [
              0,
              121
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/340"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/19"
        },
        "prov": [
          {
            "bbox": {
              "b": 336.664587509724,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.39999775,
              "r": 380.20292829477336,
              "t": 345.2522954453124
            },
            "charspan": [
              0,
              70
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/341"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/19"
        },
        "prov": [
          {
            "bbox": {
              "b": 318.30460250972396,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.39999775,
              "r": 331.921761326951,
              "t": 326.89231044531243
            },
            "charspan": [
              0,
              61
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/342"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/pct/pct-pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settleme-bf1d0d37637e/sha256-889bb5071f239ece8c2453d55be7156cab9a10554716bee2a889eeb632909774.md",
    "source_manifest_line_number": 22,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/pipeline-capacity-trading-pct/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/pipeline-capacity/2019/pct-industry-guide.pdf?rev=7bdb8fe5bd964126b87b6b65a4aeb0ab&sc_lang=en"
  },
  "content_sha256": "889bb5071f239ece8c2453d55be7156cab9a10554716bee2a889eeb632909774",
  "corpus": "pct",
  "document_family": "pct__pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settlement-prudential-arrangements-and-market-integration",
  "document_family_id": "pct__pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settlement-prudential-arrangements-and-market-integration",
  "document_identity": "pct/pct-pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settleme-bf1d0d37637e/sha256-889bb5071f239ece8c2453d55be7156cab9a10554716bee2a889eeb632909774",
  "document_title": "##### PCT Industry Guide A detailed guide to participation roles, the CTP, DAA, settlement, prudential arrangements and market integration.",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/pct/pct-pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settleme-bf1d0d37637e/sha256-889bb5071f239ece8c2453d55be7156cab9a10554716bee2a889eeb632909774/chunk-2b18ad31e3a9b165c914de0e.md",
  "heading_path": [
    "Order matching"
  ],
  "path": "generated/silver/chunks/pct/pct-pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settleme-bf1d0d37637e/sha256-889bb5071f239ece8c2453d55be7156cab9a10554716bee2a889eeb632909774/chunk-2b18ad31e3a9b165c914de0e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-pct-industry-guide-a-detailed-guide-to-participation-roles-the-ctp-daa-settleme-bf1d0d37637e/sha256-889bb5071f239ece8c2453d55be7156cab9a10554716bee2a889eeb632909774.md"
}
---

The matching process combines bids and offers for a given product based on price-time priority. Orders are first matched based on price merit, with new offers matched against the highest price bid, and new bids matched against the lowest price offer. Where two or more orders for a product have the same price and are 'in the money', the order with the earlier time is selected.
The transaction price is set at the initiator's order price. It is possible that a bid and offer may overlap in price if:
-  Orders are entered around the same time (or the pre-open period), or
-  When a participant intends to deal multiple orders at once.
