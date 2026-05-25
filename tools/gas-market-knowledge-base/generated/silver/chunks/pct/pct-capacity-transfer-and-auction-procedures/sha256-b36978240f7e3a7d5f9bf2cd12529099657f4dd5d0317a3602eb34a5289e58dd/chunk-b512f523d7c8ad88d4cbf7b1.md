---
{
  "chunk_id": "chunk-b512f523d7c8ad88d4cbf7b1",
  "chunk_ordinal": 182,
  "chunk_text_sha256": "22fc6e0777316d34c25884fdce27db82dafb53037fb7e2f06045bc8e3cbf973c",
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
              "b": 335.8387829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.58,
              "r": 478.3150400000002,
              "t": 357.8208629101563
            },
            "charspan": [
              0,
              101
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/869"
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
              "b": 276.5587829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 528.3944800000002,
              "t": 325.1808629101563
            },
            "charspan": [
              0,
              369
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/870"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/tables/17"
        },
        "prov": [
          {
            "bbox": {
              "b": 257.82548986840675,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 327.93879999999996,
              "t": 266.8399829101563
            },
            "charspan": [
              0,
              54
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/texts/871"
      },
      {
        "children": [
          {
            "$ref": "#/texts/871"
          }
        ],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 79.24444580078125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.4940185546875,
              "r": 527.200439453125,
              "t": 252.07330322265625
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 50
          }
        ],
        "self_ref": "#/tables/17"
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
              "b": 712.1526794433594,
              "coord_origin": "BOTTOMLEFT",
              "l": 66.8948974609375,
              "r": 527.324951171875,
              "t": 749.0075988769531
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 51
          }
        ],
        "self_ref": "#/tables/18"
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
  "generated_path": "generated/silver/chunks/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd/chunk-b512f523d7c8ad88d4cbf7b1.md",
  "heading_path": [
    "21.1. Indices and terms used in equations"
  ],
  "path": "generated/silver/chunks/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd/chunk-b512f523d7c8ad88d4cbf7b1.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/pct/pct-capacity-transfer-and-auction-procedures/sha256-b36978240f7e3a7d5f9bf2cd12529099657f4dd5d0317a3602eb34a5289e58dd.md"
}
---

The following table defines the indices used in the settlement equations and prudential calculations.
A reference to a connected auction product means, in relation to an auction participant for a gas day and each Auction Product for which the auction participant was allocated auction MDQ for the gas day , each other Auction Product in the auction participant's successful bid (and if there was more than one, the bid in relation to which the auction MDQ was allocated).
Table 21.1.1  Indices used in the settlement equations

ap, Definition = Denotes an auction participant .. bp, Definition = Denotes a billing period .. c, Definition = Denotes a product component. d, Definition = Denotes a gas day .. i, Definition = Denotes a bid or, in a stepped bid, a bid step within the stepped bid.. p, Definition = Denotes an Auction Product.. p*, Definition = Denotes an Auction Product within a set of connected auction products.. p1 to pk, Definition = Denotes each Auction Product within a set of connected auction products.. lp, Definition = Denotes a connected auction product.
Term, 1 = Definition. sp, 1 = Denotes a facility operator .
