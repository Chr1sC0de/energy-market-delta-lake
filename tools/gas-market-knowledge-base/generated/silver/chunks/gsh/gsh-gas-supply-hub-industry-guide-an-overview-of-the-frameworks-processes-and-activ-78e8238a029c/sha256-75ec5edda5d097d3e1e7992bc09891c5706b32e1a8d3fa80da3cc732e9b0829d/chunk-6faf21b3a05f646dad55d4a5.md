---
{
  "chunk_id": "chunk-6faf21b3a05f646dad55d4a5",
  "chunk_ordinal": 84,
  "chunk_text_sha256": "3ee5961f443014627b144a7311c3b63c0dab442f5b2abb17c91c4c79810b6c89",
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
              "b": 78.05278291015634,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.4,
              "r": 534.9772000000006,
              "t": 126.5508629101563
            },
            "charspan": [
              0,
              345
            ],
            "page_no": 25
          }
        ],
        "self_ref": "#/texts/412"
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
              "b": 718.0887829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.4,
              "r": 514.8418,
              "t": 753.2708629101563
            },
            "charspan": [
              0,
              271
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/415"
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
              "b": 673.0887829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.4,
              "r": 530.1755199999999,
              "t": 708.3908629101563
            },
            "charspan": [
              0,
              264
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/416"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d.md",
    "source_manifest_line_number": 17,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-supply-hub-gsh/exchange-agreement-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/gas_supply_hubs/market_operations/gas-supply-hub-industry-guide.pdf?rev=f1009623733543a9b53d1f088b07e225&sc_lang=en"
  },
  "content_sha256": "75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d",
  "corpus": "gsh",
  "document_family": "gsh__gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activities-of-the-gsh",
  "document_family_id": "gsh__gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activities-of-the-gsh",
  "document_identity": "gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d",
  "document_title": "##### Gas Supply Hub industry guide An overview of the frameworks, processes and activities of the GSH.",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d/chunk-6faf21b3a05f646dad55d4a5.md",
  "heading_path": [
    "5.1.2.8  Hidden Quantity"
  ],
  "path": "generated/silver/chunks/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d/chunk-6faf21b3a05f646dad55d4a5.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d.md"
}
---

The selection of the Hidden Quantity characteristic allows a participant to enter an order with a portion of the order quantity not visible to other Trading Participants. The Hidden Quantity characteristic could be used by a Trading Participant that has a relatively large order quantity that it would like released onto the exchange in parcels.
The Trading Participant enters a Hidden Quantity (GJ), which is the total of the additional gas to be made available if the order quantity is dealt. If the order is matched, a further portion of the hidden quantity (submitted order quantity) is activated on the exchange.
The Hidden Quantity can be released onto the exchange at a price different to the initial order price by submitting a value for the Hidden Qty Delta . For an offer, the order price increases by the Hidden Qty Delta if it has a positive value (vice versa for bids).
