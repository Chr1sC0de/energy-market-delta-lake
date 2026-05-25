---
{
  "chunk_id": "chunk-9f4dc8d58c9668a547a9cd0f",
  "chunk_ordinal": 110,
  "chunk_text_sha256": "22313daa6bc8f659ba6d35f8524acbfdb74a830a67b84ba9c3a9eaf4a148c769",
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
              "b": 523.1510314941406,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.14224243164062,
              "r": 524.224853515625,
              "t": 710.3871307373047
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/tables/27"
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
              "b": 493.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3927999999995,
              "t": 518.2270980273438
            },
            "charspan": [
              0,
              183
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/246"
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
              "b": 469.32501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 404.17912,
              "t": 479.2270980273438
            },
            "charspan": [
              0,
              69
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/texts/247"
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
              "b": 249.2459716796875,
              "coord_origin": "BOTTOMLEFT",
              "l": 74.42051696777344,
              "r": 522.20654296875,
              "t": 460.9089050292969
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 29
          }
        ],
        "self_ref": "#/tables/28"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-9f4dc8d58c9668a547a9cd0f.md",
  "heading_path": [
    "4.1.3.2 Initiate Change Response Transaction"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-9f4dc8d58c9668a547a9cd0f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

Trigger, • 170A TRANSFER RESPONSE = Change Request has been successfully validated by AEMO. Pre-conditions, • 170A TRANSFER RESPONSE = A valid transfer request transaction has been received.. Post-conditions, • 170A TRANSFER RESPONSE = A Change Response is sent to the Market Participant who submitted the Initiate Transfer Request.. Transaction acknowledgment specific event codes, • 170A TRANSFER RESPONSE = None
A  Change  Response  is  sent  to  the  Market  Participant  who  submitted  the  Initiate  Transfer Request to indicate that the transfer request is in progress for the Supply Point.
The following data elements are to be supplied with this transaction:
RequestID, TRANSACTION:.Received From:.Sent To:.Mandatory / Optional / Not Required = M. RequestID, CATSCHANGERESPONSE.AEMO.New FRO.Usage = The unique ID assigned by AEMO to the Change Request. Event, TRANSACTION:.Received From:.Sent To:.Mandatory / Optional / Not Required = M. Event, CATSCHANGERESPONSE.AEMO.New FRO.Usage = At least event code must be supplied, other elements are optional
