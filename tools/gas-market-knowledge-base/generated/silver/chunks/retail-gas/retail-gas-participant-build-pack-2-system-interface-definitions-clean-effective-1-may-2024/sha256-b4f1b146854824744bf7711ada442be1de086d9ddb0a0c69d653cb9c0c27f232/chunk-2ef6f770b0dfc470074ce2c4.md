---
{
  "chunk_id": "chunk-2ef6f770b0dfc470074ce2c4",
  "chunk_ordinal": 242,
  "chunk_text_sha256": "bab7e5d286a871acda387ed4e4d73104537f13b3087fcf35352233aebff762bf",
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
              "b": 92.59901095552061,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.6356,
              "t": 132.49709802734378
            },
            "charspan": [
              0,
              278
            ],
            "page_no": 94
          }
        ],
        "self_ref": "#/texts/1119"
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
              "b": 701.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.5104799999996,
              "t": 741.4570980273437
            },
            "charspan": [
              0,
              266
            ],
            "page_no": 95
          }
        ],
        "self_ref": "#/texts/1123"
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
              "b": 662.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3927999999995,
              "t": 687.4570980273437
            },
            "charspan": [
              0,
              108
            ],
            "page_no": 95
          }
        ],
        "self_ref": "#/texts/1124"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-2ef6f770b0dfc470074ce2c4.md",
  "heading_path": [
    "4.4.2.1 Meter Fix Notification Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-2ef6f770b0dfc470074ce2c4.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Using the Meter Identification Registration Number  (MIRN),  AEMO  will  validate  the GasMeterNotification/MeterFix  and  if  the  Current  FRO  is  the  same  as  the  Declared  Host Retailer for that distribution network then AEMO will nack the transaction (event code 3415).
Using  the  NetworkId  AEMO  will  validate  the  GasMeterNotification/MeterFix  and  if  the NetworkId is not a valid NetworkId then AEMO will nack the transaction (event code 3416). A valid NetworkID is either '00' '<Blank>' or a NetworkId number assigned by AEMO.
The  following  data  elements  are  to  be  supplied  with  the  GasMeterNotification/MeterFix transaction.
