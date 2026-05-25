---
{
  "chunk_id": "chunk-95bf7417d7e6e77a6cfc46b9",
  "chunk_ordinal": 178,
  "chunk_text_sha256": "a9455d007558faa9ce830c856016ca9bf66acdac3604ec67794eb95e71925696",
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
              "b": 249.8250109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.6173599999998,
              "t": 304.7270980273438
            },
            "charspan": [
              0,
              326
            ],
            "page_no": 61
          }
        ],
        "self_ref": "#/texts/708"
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
              "b": 225.8250109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 452.53912,
              "t": 235.7270980273438
            },
            "charspan": [
              0,
              80
            ],
            "page_no": 61
          }
        ],
        "self_ref": "#/texts/709"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/1"
        },
        "prov": [
          {
            "bbox": {
              "b": 201.79501095552064,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 488.80912,
              "t": 211.69709802734383
            },
            "charspan": [
              0,
              83
            ],
            "page_no": 61
          }
        ],
        "self_ref": "#/texts/710"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/1"
        },
        "prov": [
          {
            "bbox": {
              "b": 147.79501095552064,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5603999999998,
              "t": 187.69709802734383
            },
            "charspan": [
              0,
              256
            ],
            "page_no": 61
          }
        ],
        "self_ref": "#/texts/711"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-95bf7417d7e6e77a6cfc46b9.md",
  "heading_path": [
    "4.1.11 Delivering Problem Notice"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-95bf7417d7e6e77a6cfc46b9.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The Problem Notice described in this section is responsible for conveying change information to the Market Participant (New FRO) who initiated the Change Request. The sender of the Problem Notice may include whatever text they like in the Event associated with the notice and AEMO will pass the Event unaltered to the New FRO.
There are two triggers that result in a Problem Notice being initiated. They are
1. the Current FRO or Distributor initiating a Problem Notice (CATSChangeAlert); or
2. or  as  a  result  of  receiving  a  NegativeAcknowledgment  (NAK)  to  a  CATSNotification transaction, containing specific event codes, from either the Current FRO or Distributor, AEMO will generate  a Problems Notice (CATSChangeAlert) to the New FRO.
