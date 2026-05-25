---
{
  "chunk_id": "chunk-fad1036446bcf8e515f139db",
  "chunk_ordinal": 275,
  "chunk_text_sha256": "4d34e8ae1fab221efc9f9afa9938d4540bd320292f2354622278ca9182478466",
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
              "b": 71.049560546875,
              "coord_origin": "BOTTOMLEFT",
              "l": 79.43029022216797,
              "r": 803.0468139648438,
              "t": 500.3223876953125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 109
          }
        ],
        "self_ref": "#/tables/116"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-fad1036446bcf8e515f139db.md",
  "heading_path": [
    "A.1 aseXML Data Elements 1"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-fad1036446bcf8e515f139db.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

BaseLoad, TABLE OF TRANSACTIONS ELEMENT NAME = Base Load. BaseLoad, DESCRIPTION = Non weather sensitive Gas usage per day (MJ). BaseLoad, ATTRIBUTES /FORMAT = Decimal. BaseLoad, LENGTH/ DECIMAL PLACES = 9,1. BaseLoad, ALLOWED VALUES = . ChangeReasonCode, TABLE OF TRANSACTIONS ELEMENT NAME = Change Reason Code. ChangeReasonCode, DESCRIPTION = Identifies the type of transfer request. ChangeReasonCode, ATTRIBUTES /FORMAT = String. ChangeReasonCode, LENGTH/ DECIMAL PLACES = 4. ChangeReasonCode, ALLOWED VALUES = '0001' = Prospective transfer, in situ '0002' = Prospective transfer, move-in '0003' = Retrospective transfer. ChangeStatusCode, TABLE OF TRANSACTIONS ELEMENT NAME = Change Status Code. ChangeStatusCode, DESCRIPTION = Describes the status of a transfer request within CATS. ChangeStatusCode, ATTRIBUTES /FORMAT = String. ChangeStatusCode, LENGTH/ DECIMAL PLACES = 4. ChangeStatusCode, ALLOWED VALUES = 'REQ' = Requested 'PEN' = Pending 'OBJ' = Objected 'COM' = Completed 'CAN' = Cancelled "RCA" = RoLR Cancelled 'RCO" = RoLR
