---
{
  "chunk_id": "chunk-adf502023f366408adbce24d",
  "chunk_ordinal": 224,
  "chunk_text_sha256": "0b66d7c75de6d1e148d6d21d3d24da8b1ccf24bc0a898ab728e5587bc90c2e4a",
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
              "b": 129.43501095552062,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.69872,
              "t": 184.3370980273438
            },
            "charspan": [
              0,
              340
            ],
            "page_no": 86
          }
        ],
        "self_ref": "#/texts/1021"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/pictures/118"
        },
        "prov": [
          {
            "bbox": {
              "b": 484.20501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.4569599999999,
              "t": 509.1070980273438
            },
            "charspan": [
              0,
              90
            ],
            "page_no": 87
          }
        ],
        "self_ref": "#/texts/1025"
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
              "b": 460.20501095552055,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 422.53912,
              "t": 470.1070980273438
            },
            "charspan": [
              0,
              70
            ],
            "page_no": 87
          }
        ],
        "self_ref": "#/texts/1042"
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
              "b": 281.38501095552056,
              "coord_origin": "BOTTOMLEFT",
              "l": 70.944,
              "r": 527.4895999999999,
              "t": 306.28709802734375
            },
            "charspan": [
              0,
              97
            ],
            "page_no": 87
          }
        ],
        "self_ref": "#/texts/1047"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-adf502023f366408adbce24d.md",
  "heading_path": [
    "4.3.3 Ad-hoc Refresh of Base Load and Temperature Sensitivity Factor"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232/chunk-adf502023f366408adbce24d.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-2-system-interface-definitions-clean-effective-1-may-2024/sha256-b4f1b146854824744bf7711ada442be1de086d9ddb0a0c69d653cb9c0c27f232.md"
}
---

The transaction is used to refresh Base Load (BL) and Temperature Sensitivity Factor (TSF) data for basic meter sites stored by AEMO. Distributor will supply the ad-hoc data as a CSV file encapsulated inside a NMIStandingDataUpdateNotification aseXML transaction. Bi-annual refresh and response will be delivered by means other than aseXML.
FIGURE  4-29.  BASE  LOAD  AND  TEMPERATURE  SENSITIVITY  FACTOR  REFRESH ACTIVITY DIAGRAM
The process flow above translates into the following sequence diagram.
FIGURE  4-30.  AD-HOC  BASE  LOAD  AND  TEMPERATURE  SENSITIVITY  FACTOR REFRESH SEQUENCE DIAGRAM
