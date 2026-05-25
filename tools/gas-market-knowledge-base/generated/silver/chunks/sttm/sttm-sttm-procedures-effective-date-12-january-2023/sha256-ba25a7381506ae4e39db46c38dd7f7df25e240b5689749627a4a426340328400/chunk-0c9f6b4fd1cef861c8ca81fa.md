---
{
  "chunk_id": "chunk-0c9f6b4fd1cef861c8ca81fa",
  "chunk_ordinal": 304,
  "chunk_text_sha256": "88cb9deffa56c2f2cbc7b9ace9e80ff17fb8241939594ed44480e2fba61dd93e",
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
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/141"
        },
        "prov": [
          {
            "bbox": {
              "b": 453.66745826927234,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 514.37272,
              "t": 476.40086291015626
            },
            "charspan": [
              0,
              155
            ],
            "page_no": 77
          }
        ],
        "self_ref": "#/texts/1167"
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
              "b": 420.9074582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 451.0652800000002,
              "t": 442.08086291015627
            },
            "charspan": [
              0,
              101
            ],
            "page_no": 77
          }
        ],
        "self_ref": "#/texts/1168"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/142"
        },
        "prov": [
          {
            "bbox": {
              "b": 389.5874582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 506.6026,
              "t": 412.3208629101563
            },
            "charspan": [
              0,
              154
            ],
            "page_no": 77
          }
        ],
        "self_ref": "#/texts/1169"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "formula",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 356.80745826927233,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 457.63888000000003,
              "t": 378.0008629101563
            },
            "charspan": [
              0,
              109
            ],
            "page_no": 77
          }
        ],
        "self_ref": "#/texts/1170"
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
              "b": 327.92962931899604,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 523.2430000000002,
              "t": 348.4819829101563
            },
            "charspan": [
              0,
              137
            ],
            "page_no": 77
          }
        ],
        "self_ref": "#/texts/1171"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md",
    "source_manifest_line_number": 43,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-procedures-v134.pdf?rev=f9d5cb1606a240bbb8a3701d76eb7a2f&sc_lang=en"
  },
  "content_sha256": "ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-12-january-2023",
  "document_family_id": "sttm__sttm-procedures-effective-date-12-january-2023",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400",
  "document_title": "##### STTM Procedures Effective date 12 January 2023",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-0c9f6b4fd1cef861c8ca81fa.md",
  "heading_path": [
    "10.7.4. Restoration of MOS gas"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-0c9f6b4fd1cef861c8ca81fa.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

- (c) The MOS cash-out payment for the hub for Trading Participant p for providing overrun MOS at the gas day d price for MOS gas provided on gas day d-2 is:
MCOP(p,d) = HP(d)×  k  SP[  ct(k)MAX(0,OMAQ S (p,d-2,ct(k))) +  cf(k)MAX(0,OMAQ S (p,d-2,cf(k)))]
- (d) The MOS cash-out charge for the hub for Trading Participant p for providing overrun MOS at the gas day d price for MOS gas provided on gas day d-2 is:
<!-- formula-not-decoded -->
Note : Whether a payment or charge applies depends on whether the change in net gas allocated to flow to the hub is positive or negative.
