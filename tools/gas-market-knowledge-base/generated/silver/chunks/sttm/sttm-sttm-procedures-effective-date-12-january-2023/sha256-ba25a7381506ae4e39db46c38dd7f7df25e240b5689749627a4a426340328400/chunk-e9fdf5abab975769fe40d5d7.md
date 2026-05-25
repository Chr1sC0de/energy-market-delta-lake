---
{
  "chunk_id": "chunk-e9fdf5abab975769fe40d5d7",
  "chunk_ordinal": 272,
  "chunk_text_sha256": "4ab579a74a2395e964fd1de30ac852bef9fcc5b5ce3c64bf9e40d763985f2429",
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
              "b": 710.3774582692722,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 472.06888000000004,
              "t": 719.3108629101563
            },
            "charspan": [
              0,
              86
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/1004"
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
              "b": 689.8574582692722,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 338.35888,
              "t": 698.7908629101563
            },
            "charspan": [
              0,
              38
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/1005"
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
              "b": 660.9796293189961,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 525.3530000000002,
              "t": 681.4119829101563
            },
            "charspan": [
              0,
              173
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/1006"
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
              "b": 580.4596293189961,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 526.2640000000002,
              "t": 650.5719829101563
            },
            "charspan": [
              0,
              543
            ],
            "page_no": 70
          }
        ],
        "self_ref": "#/texts/1007"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-e9fdf5abab975769fe40d5d7.md",
  "heading_path": [
    "10.5.2. Variation quantity"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-e9fdf5abab975769fe40d5d7.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

The total GJ variation quantity for Trading Participant p on gas day d for the hub is:
<!-- formula-not-decoded -->
Note: This is the absolute value of the component of the cumulative changes to the market schedule due to market schedule variations which are subject to variation charge s.
Note : Each Trading Participant will have a single variation quantity (in GJ) for a hub for a gas day .  If the Trading Participant is both an STTM User and an STTM Shipper hauling from the hub , then VQ(p, d) will reflect the net change in its withdrawals from the hub that are subject to variation changes.  The actual total change in its market schedule (inclusive of all its market schedule variations ) may be different, as MSVs which do not incur a charge (because they imply no net change in hub withdrawal) are not included in VQ(p,d).
