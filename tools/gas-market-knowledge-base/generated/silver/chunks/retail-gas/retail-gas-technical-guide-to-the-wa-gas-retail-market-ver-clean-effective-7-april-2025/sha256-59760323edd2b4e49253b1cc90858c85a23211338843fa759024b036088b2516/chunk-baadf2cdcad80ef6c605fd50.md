---
{
  "chunk_id": "chunk-baadf2cdcad80ef6c605fd50",
  "chunk_ordinal": 63,
  "chunk_text_sha256": "653705debe9c834de26f93cf58c03c56657cf07619821879d4ecbd422bd5b5f7",
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
              "b": 177.389387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 525.6463199999998,
              "t": 198.3108629101563
            },
            "charspan": [
              0,
              155
            ],
            "page_no": 23
          }
        ],
        "self_ref": "#/texts/499"
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
              "b": 147.149387390808,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 498.22643999999985,
              "t": 168.07086291015628
            },
            "charspan": [
              0,
              146
            ],
            "page_no": 23
          }
        ],
        "self_ref": "#/texts/500"
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
              "b": 129.0293873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 335.56899999999996,
              "t": 137.83086291015627
            },
            "charspan": [
              0,
              58
            ],
            "page_no": 23
          }
        ],
        "self_ref": "#/texts/501"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516/chunk-baadf2cdcad80ef6c605fd50.md",
  "heading_path": [
    "6.2.3. Converting a Standard Volume to Energy"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516/chunk-baadf2cdcad80ef6c605fd50.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-technical-guide-to-the-wa-gas-retail-market-ver-clean-effective-7-april-2025/sha256-59760323edd2b4e49253b1cc90858c85a23211338843fa759024b036088b2516.md"
}
---

Once the standard volume has been calculated, it is possible to convert that standard volume to energy (joules) using a factor called Heating Value ('HV').
The HV represents the energy per unit of volume of gas. The energy value of gas is calculated by multiplying the HV of gas by the standard volume.
That is: Energy = Heating Value (HV) x Standard Volume (V)
