---
{
  "chunk_id": "chunk-ad730fe8fa69d512f8a7aecd",
  "chunk_ordinal": 105,
  "chunk_text_sha256": "bfd48f221c10dd5d49f05be7d02ef55f01afa5a533421d5c1bb7cc40d19a0232",
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
              "b": 473.4987829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.58,
              "r": 517.879,
              "t": 482.1608629101563
            },
            "charspan": [
              0,
              97
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/504"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/53"
        },
        "prov": [
          {
            "bbox": {
              "b": 414.3387829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 521.5393600000003,
              "t": 462.84086291015626
            },
            "charspan": [
              0,
              362
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/505"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/53"
        },
        "prov": [
          {
            "bbox": {
              "b": 381.67878291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 528.3230800000002,
              "t": 403.6608629101563
            },
            "charspan": [
              0,
              107
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/506"
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
              "b": 362.35878291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 218.05904,
              "t": 371.02086291015627
            },
            "charspan": [
              0,
              16
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/507"
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
              "b": 343.03878291015627,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 162.94904,
              "t": 351.7008629101563
            },
            "charspan": [
              0,
              6
            ],
            "page_no": 30
          }
        ],
        "self_ref": "#/texts/508"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd.md",
    "source_manifest_line_number": 19,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/pipeline-capacity-trading-pct/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/pipeline-capacity/capacity-transfer-and-auction-procedures.pdf?rev=005d6f733a6d4eefb42e02aa7b7fc16a&sc_lang=en"
  },
  "content_sha256": "b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd",
  "corpus": "pct",
  "document_family": "pct__capacity-transfer-and-auction-procedures",
  "document_family_id": "pct__capacity-transfer-and-auction-procedures",
  "document_identity": "pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd",
  "document_title": "##### Capacity transfer and auction procedures",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd/chunk-ad730fe8fa69d512f8a7aecd.md",
  "heading_path": [
    "10.4. Calculation of payments"
  ],
  "path": "generated/silver/chunks/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd/chunk-ad730fe8fa69d512f8a7aecd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd.md"
}
---

Rule 639(7) requires AEMO to specify the methodology for calculating service continuity payments.
- (a) For rule 639(7), the amount payable by AEMO to the facility operator for the provision of transportation services during the applicable service continuity period in accordance with rule 639(2) is the sum, for each gas day in the service continuity period, of the daily service continuity payments for that gas day determined in accordance with paragraph (b).
- (b) AEMO must determine the daily service continuity payment for each gas day and capacity type as follows:
DSCP = TC x WATP
where:
