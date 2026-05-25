---
{
  "chunk_id": "chunk-bae601b3dddeec887d25fd2e",
  "chunk_ordinal": 451,
  "chunk_text_sha256": "03feaba83683c3eff3ed6828e9eeb5a0b6e60ce1298de485fe9f4592b0dba3a1",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/308"
        },
        "prov": [
          {
            "bbox": {
              "b": 123.43501583833313,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 478.84911999999997,
              "t": 133.33710291015632
            },
            "charspan": [
              0,
              68
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2290"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/308"
        },
        "prov": [
          {
            "bbox": {
              "b": 110.8350158383331,
              "coord_origin": "BOTTOMLEFT",
              "l": 160.22,
              "r": 314.39912,
              "t": 120.7371029101563
            },
            "charspan": [
              0,
              29
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2291"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/308"
        },
        "prov": [
          {
            "bbox": {
              "b": 98.1190158383331,
              "coord_origin": "BOTTOMLEFT",
              "l": 191.93,
              "r": 431.17912,
              "t": 108.02110291015629
            },
            "charspan": [
              0,
              48
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2292"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/308"
        },
        "prov": [
          {
            "bbox": {
              "b": 85.51901583833308,
              "coord_origin": "BOTTOMLEFT",
              "l": 191.93,
              "r": 467.20912,
              "t": 95.42110291015626
            },
            "charspan": [
              0,
              54
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2293"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/308"
        },
        "prov": [
          {
            "bbox": {
              "b": 72.79901583833305,
              "coord_origin": "BOTTOMLEFT",
              "l": 191.93,
              "r": 463.36912,
              "t": 82.70110291015635
            },
            "charspan": [
              0,
              54
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2294"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365.md",
    "source_manifest_line_number": 33,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/new-south-wales-and-act",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/nsw-act/2025/retail-market-procedures-nswact-v-30-clean.pdf?rev=d79faf1b746a4a3190cb1338f2e7bc98&sc_lang=en"
  },
  "content_sha256": "99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365",
  "corpus": "retail_gas",
  "document_family": "retail-gas__retail-market-procedures-nswact-ver-clean-effective-3-march-2025",
  "document_family_id": "retail-gas__retail-market-procedures-nswact-ver-clean-effective-3-march-2025",
  "document_identity": "retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365",
  "document_title": "##### Retail Market Procedures (NSWACT) ver - (clean) Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365/chunk-bae601b3dddeec887d25fd2e.md",
  "heading_path": [
    "(d) Calculation for ACT"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365/chunk-bae601b3dddeec887d25fd2e.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365.md"
}
---

- (i) The effective degree day (EDD) for ACT is calculated as follows:
- EDD = DD (temperature effect)
+ 0.0163 x DD x average wind (wind chill factor)
- 0.1326 x sunshine hours (warming effect of sunshine)
+ 3.1277 x Cos ((2π(day-195)) / 365) (seasonal factor)
