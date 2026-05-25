---
{
  "chunk_id": "chunk-ced3cab161fef52b6d8a6913",
  "chunk_ordinal": 305,
  "chunk_text_sha256": "8859a3c7374f0370804ec68bc4956198758b7109f2ab313715b782229e2c7a4f",
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
              "b": 622.9550109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5530399999997,
              "t": 722.8570980273438
            },
            "charspan": [
              0,
              583
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/texts/1330"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/6"
        },
        "prov": [
          {
            "bbox": {
              "b": 568.9250109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 88.944,
              "r": 527.4475999999994,
              "t": 608.8570980273438
            },
            "charspan": [
              0,
              224
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/texts/1331"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/6"
        },
        "prov": [
          {
            "bbox": {
              "b": 514.9250109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 88.944,
              "r": 527.5090399999997,
              "t": 554.8270980273437
            },
            "charspan": [
              0,
              256
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/texts/1332"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/6"
        },
        "prov": [
          {
            "bbox": {
              "b": 490.9250109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 88.944,
              "r": 524.83024,
              "t": 500.8270980273438
            },
            "charspan": [
              0,
              92
            ],
            "page_no": 123
          }
        ],
        "self_ref": "#/texts/1333"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md",
    "source_manifest_line_number": 31,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-2--system-interface-definitions-v-36-clean.pdf?rev=0420b92c0a5e4d879175ec3003826d7d&sc_lang=en"
  },
  "content_sha256": "b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_family_id": "retail-gas__participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232",
  "document_title": "##### Participant Build Pack 2 - System Interface Definitions (Clean) Effective 1 May 2024",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-ced3cab161fef52b6d8a6913.md",
  "heading_path": [
    "A.3 Decimal Datatypes"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-ced3cab161fef52b6d8a6913.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Participant Build Packs refer to Numeric or Decimal datatype for numbers that include decimal points. Normally, the data is packed to conserve disk space, and preserves its accuracy to the least significant digit after arithmetic operations. The numeric datatypes are defined with two optional parameters, precision and scale, enclosed in parentheses and separated by a comma: numeric [( precision [, scale ])] . The precision (referred to in this document as "length") and scale (referred to as "decimal places") determine the range of values that can be stored in a numeric column.
- The precision specifies the maximum number of decimal digits that can be stored in the column. It includes all digits, both to the right and to the left of the decimal point. Precisions can range from 1 digit to 38 digits.
- The scale specifies the maximum number of digits that can be stored to the right of the decimal point. The scale must be less than or equal to the precision. You can specify a scale ranging from 0 digits to 38 digits or use the default scale of 0 digits.
- The number of digits to the left of the decimal point cannot exceed the precision - scale.
