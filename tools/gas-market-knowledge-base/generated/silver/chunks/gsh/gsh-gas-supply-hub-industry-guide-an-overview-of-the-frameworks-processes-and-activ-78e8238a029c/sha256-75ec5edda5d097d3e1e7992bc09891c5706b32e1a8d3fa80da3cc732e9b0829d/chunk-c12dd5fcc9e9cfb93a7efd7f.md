---
{
  "chunk_id": "chunk-c12dd5fcc9e9cfb93a7efd7f",
  "chunk_ordinal": 97,
  "chunk_text_sha256": "4e5b63ba5e17ac5e80842e178f3db9a1e089056fedc45602e4a2e0472c52b17c",
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
              "b": 604.4487829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.4,
              "r": 511.3868400000001,
              "t": 626.4308629101563
            },
            "charspan": [
              0,
              161
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/texts/487"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "caption",
        "parent": {
          "$ref": "#/tables/12"
        },
        "prov": [
          {
            "bbox": {
              "b": 577.9443566676116,
              "coord_origin": "BOTTOMLEFT",
              "l": 62.4,
              "r": 333.77,
              "t": 586.0899829101563
            },
            "charspan": [
              0,
              57
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/texts/488"
      },
      {
        "children": [
          {
            "$ref": "#/texts/488"
          }
        ],
        "content_layer": "body",
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 487.3169860839844,
              "coord_origin": "BOTTOMLEFT",
              "l": 61.52634811401367,
              "r": 532.8964233398438,
              "t": 572.0317687988281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 28
          }
        ],
        "self_ref": "#/tables/12"
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
  "generated_path": "generated/silver/chunks/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d/chunk-c12dd5fcc9e9cfb93a7efd7f.md",
  "heading_path": [
    "5.2.2.1  Order matching example"
  ],
  "path": "generated/silver/chunks/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d/chunk-c12dd5fcc9e9cfb93a7efd7f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gsh/gsh-gas-supply-hub-industry-guide-an-overview-of-the-frameworks-processes-and-activ-78e8238a029c/sha256-75ec5edda5d097d3e1e7992bc09891c5706b32e1a8d3fa80da3cc732e9b0829d.md"
}
---

Once the transaction has been formed, all of Buyer G's order quantity has been matched but 2,000 GJ of Seller C's order remains active as shown below in Table 6.
Table 6 Example order matching -resultant bid offer stack

F, Qty (GJ) = 4,000. F, Price ($/GJ) = 3.00. F, Price ($/GJ) = 5.00. F, Qty (GJ) = 2,000. F, Seller = C. E, Qty (GJ) = 1,000. E, Price ($/GJ) = 1.00. E, Price ($/GJ) = 6.00. E, Qty (GJ) = 4,000. E, Seller = B. , Qty (GJ) = . , Price ($/GJ) = . , Price ($/GJ) = 8.00. , Qty (GJ) = 2,000. , Seller = A
