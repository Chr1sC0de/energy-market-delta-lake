---
{
  "chunk_id": "chunk-882c20a4ffc30fd4f50775ea",
  "chunk_ordinal": 279,
  "chunk_text_sha256": "c43b440576f019322e85b53e15e5536ad5dd2241ee223906cac10af9dbffe1f4",
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
              "b": 287.12962931899597,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 527.9229999999999,
              "t": 357.2419829101563
            },
            "charspan": [
              0,
              585
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1042"
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
              "b": 268.64962931899606,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 476.962,
              "t": 276.7219829101564
            },
            "charspan": [
              0,
              88
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1043"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/117"
        },
        "prov": [
          {
            "bbox": {
              "b": 235.36745826927233,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 517.00684,
              "t": 258.10086291015637
            },
            "charspan": [
              0,
              101
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1044"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-882c20a4ffc30fd4f50775ea.md",
  "heading_path": [
    "10.5.4. Allocation to steps -Quantity method"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-882c20a4ffc30fd4f50775ea.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

Note: That is, the total of variations is assigned to steps, where each step is an absolute GJ quantity.  Thus if the raw variation is -50GJ and the step boundaries are 10GJ, 60GJ and 80GJ then VQ(p,d) = ABS(-50) or 50, GVarU(p,d,1) = min(50,10) = 10, GVarU(p,d,2) = min(50,60) - 10 = 40, and GVarU(p,d,3) = min(50,80) - 10 - 40 = 0.  Thus the total of market schedule variations of 50 is allocated into 3 steps of 10, 40 and 0.  In the variation charge calculation, each of these steps is settled using its factor (GVarF(f) <1) and is applied to the ex ante market price for the hub .
The last step (with f = Maxf) has the otherwise unassigned variation associated with it.
- (b) The GJ variation charge to Trading Participant p for market schedule variations for gas day d is:
