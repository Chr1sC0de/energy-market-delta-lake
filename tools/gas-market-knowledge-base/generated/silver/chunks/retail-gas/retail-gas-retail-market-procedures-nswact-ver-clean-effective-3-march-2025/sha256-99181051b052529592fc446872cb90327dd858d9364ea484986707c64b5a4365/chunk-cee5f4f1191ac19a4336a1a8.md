---
{
  "chunk_id": "chunk-cee5f4f1191ac19a4336a1a8",
  "chunk_ordinal": 449,
  "chunk_text_sha256": "417811a1793a3eb52306dadf5b495a4ab9742904f8cf3c31ffb98c217f0e3fc9",
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
              "b": 526.565015838333,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 504.8532799999994,
              "t": 561.9071029101563
            },
            "charspan": [
              0,
              172
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2273"
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
              "b": 506.76501583833306,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 376.57912,
              "t": 516.6671029101562
            },
            "charspan": [
              0,
              51
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2274"
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
              "b": 487.20501583833305,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 336.37912,
              "t": 497.1071029101563
            },
            "charspan": [
              0,
              36
            ],
            "page_no": 139
          }
        ],
        "self_ref": "#/texts/2275"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365/chunk-cee5f4f1191ac19a4336a1a8.md",
  "heading_path": [
    "(c) Sunshine hours for NSW"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365/chunk-cee5f4f1191ac19a4336a1a8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-retail-market-procedures-nswact-ver-clean-effective-3-march-2025/sha256-99181051b052529592fc446872cb90327dd858d9364ea484986707c64b5a4365.md"
}
---

Where there is no physical sensor to obtain sunshine hour values, these are derived from meter and synoptic data based on cloud cover at the specified weather stations (s).
This is achieved through the following calculation:
@hrlyssm = @psm * @percentsun * 0.01
