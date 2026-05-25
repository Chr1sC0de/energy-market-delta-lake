---
{
  "chunk_id": "chunk-3db09fb89b5070b19ceabefe",
  "chunk_ordinal": 124,
  "chunk_text_sha256": "a6771d9f8f2325051422c4a08c4b63ab035b50ef1f355dd4249532070386a0d4",
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
              "b": 435.72501095552053,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.3375999999995,
              "t": 460.6270980273438
            },
            "charspan": [
              0,
              148
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/texts/295"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 102.67501095552063,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 482.32912,
              "t": 112.57709802734382
            },
            "charspan": [
              0,
              64
            ],
            "page_no": 34
          }
        ],
        "self_ref": "#/texts/329"
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
              "b": 671.5550109555205,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.67952,
              "t": 741.4570980273437
            },
            "charspan": [
              0,
              444
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/texts/333"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 451.56501095552056,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 494.44912,
              "t": 461.4670980273438
            },
            "charspan": [
              0,
              64
            ],
            "page_no": 35
          }
        ],
        "self_ref": "#/texts/342"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-3db09fb89b5070b19ceabefe.md",
  "heading_path": [
    "4.1.5 Alternative Transfer Date"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-3db09fb89b5070b19ceabefe.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The Market Participant who initiated the transfer request may update the Proposed Transfer Date of the request during the predetermined time period.
FIGURE 4-7. PROVIDING ALTERNATIVE TRANSFER DATE ACTIVITY DIAGRAM
When the Market Participant requests a Proposed Transfer Date change, the sequence below takes  place.  Alternative  transfer  date  is  submitted  via  the  CATSChangeRequest  aseXML transaction.  Following  the  processing  of  the  request,  AEMO  issues  notifications  to  other Organisations assigned to a role for the Change Request and sends an update response to the Market Participant (New FRO) who issued the original Change Request.
FIGURE 4-8. PROVIDING ALTERNATIVE TRANSFER DATE SEQUENCE DIAGRAM
