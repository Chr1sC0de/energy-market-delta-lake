---
{
  "chunk_id": "chunk-b5af3cc68bcc492ce9ea6dcd",
  "chunk_ordinal": 223,
  "chunk_text_sha256": "d0163cd5b5dc46d50e9da079cddd23be8851aa00d0d139448b16c2fc58ae39d3",
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
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 359.790771484375,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.17816925048828,
              "r": 522.0936889648438,
              "t": 508.6263122558594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/tables/96"
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
              "b": 291.4650109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.66608,
              "t": 331.3670980273438
            },
            "charspan": [
              0,
              254
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1018"
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
              "b": 222.4650109555206,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.6670399999998,
              "t": 277.3670980273438
            },
            "charspan": [
              0,
              308
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1019"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-b5af3cc68bcc492ce9ea6dcd.md",
  "heading_path": [
    "4.3.2.2 Meter Data History Response Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-b5af3cc68bcc492ce9ea6dcd.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Trigger, 48 ENERGY HISTORY RESPONSE = Receipt of an energy history request from AEMO.. Pre-conditions, 48 ENERGY HISTORY RESPONSE = None.. Post-conditions, 48 ENERGY HISTORY RESPONSE = AEMO has obtained historic data.. Transaction acknowledgment specific event codes, 48 ENERGY HISTORY RESPONSE = None
The  Meter  Data  Gas  History  Response  is  realised  in  terms  of  the  MeterDataNotification aseXML transaction. It is used by the Distributor to deliver energy history data to AEMO. For MeterDataNotification transaction details see section 4.2.2.2.
For consistency with other energy data transactions, upon the completion of the embedded CSV  files  processing,  the  energy  history  response  transaction  will  be  confirmed  with MeterDataResponse, see section  4.2.2  for  details.  The  MeterDataResponse  transaction  is described in section 4.2.2.3.
