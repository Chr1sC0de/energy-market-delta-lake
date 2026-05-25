---
{
  "chunk_id": "chunk-f8681dd0ff1daf4f79f70ade",
  "chunk_ordinal": 57,
  "chunk_text_sha256": "a08d4c89a527fc6138fdd78fd6ab498f171dd7aec559a182a28d048a58c60c44",
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
              "b": 133.70938739080805,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 523.73216,
              "t": 171.5508629101563
            },
            "charspan": [
              0,
              195
            ],
            "page_no": 8
          }
        ],
        "self_ref": "#/texts/192"
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
              "b": 113.18938739080806,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 231.149,
              "t": 121.99086291015624
            },
            "charspan": [
              0,
              29
            ],
            "page_no": 8
          }
        ],
        "self_ref": "#/texts/193"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "footnote",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 68.4922973704414,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 329.741,
              "t": 76.41310291015634
            },
            "charspan": [
              0,
              71
            ],
            "page_no": 8
          }
        ],
        "self_ref": "#/texts/194"
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
              "b": 654.1681976318359,
              "coord_origin": "BOTTOMLEFT",
              "l": 101.99240112304688,
              "r": 526.7000732421875,
              "t": 749.0755004882812
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 9
          }
        ],
        "self_ref": "#/tables/7"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md",
    "source_manifest_line_number": 41,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-participant-build-pack-business-validations-addendum-v81.pdf?rev=eec7a7dd84b947f7af5164f757b8f62e&sc_lang=en"
  },
  "content_sha256": "a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3",
  "corpus": "sttm",
  "document_family": "sttm__sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3",
  "document_title": "##### STTM Participant Build Pack Business Validations Addendum Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-f8681dd0ff1daf4f79f70ade.md",
  "heading_path": [
    "2.1. STTM CSV transactions"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3/chunk-f8681dd0ff1daf4f79f70ade.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-participant-build-pack-business-validations-addendum-effective-date-3-march-2025/sha256-a4566ce1fc8162e8191bfc8f629612758f2be0e53ec6ad88706b1457557e7ad3.md"
}
---

For example, in the following Price Taker Bid transaction SWEXIE would accept the transaction and automatically save the first three values only. The additional 'quantity' field would be ignored:
gasdate,trn,quantity,quantity
1  Referenced to the Rules and Procedures as applicable on 3 March 2025
2009-02-12,ABCD123456,10000,20000 = In the following example, the Price Taker Bid transaction would be rejected due to the missing data for the additional 'quantity' field:. 2009-02-12,ABCD123456,10000,20000 = gasdate,trn,quantity,quantity. 2009-02-12,ABCD123456,10000,20000 = 2009-02-12,ABCD123456,10000
