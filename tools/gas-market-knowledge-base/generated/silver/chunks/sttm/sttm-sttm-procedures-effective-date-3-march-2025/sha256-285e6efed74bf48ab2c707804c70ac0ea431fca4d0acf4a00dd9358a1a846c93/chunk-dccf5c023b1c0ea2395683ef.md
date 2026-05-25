---
{
  "chunk_id": "chunk-dccf5c023b1c0ea2395683ef",
  "chunk_ordinal": 287,
  "chunk_text_sha256": "ff8b653a99cf68bb5da43465fc8f348f184e384e60aa6fd14106f82ce266abb7",
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
              "b": 672.7388423806248,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 527.6960000000005,
              "t": 745.9719829101563
            },
            "charspan": [
              0,
              582
            ],
            "page_no": 84
          }
        ],
        "self_ref": "#/texts/1316"
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
              "b": 653.6588423806247,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 473.69500000000005,
              "t": 661.6119829101563
            },
            "charspan": [
              0,
              88
            ],
            "page_no": 84
          }
        ],
        "self_ref": "#/texts/1317"
      },
      {
        "children": [],
        "content_layer": "body",
        "label": "list_item",
        "parent": {
          "$ref": "#/groups/153"
        },
        "prov": [
          {
            "bbox": {
              "b": 619.0693873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 103.46,
              "r": 515.3082800000001,
              "t": 642.2708629101563
            },
            "charspan": [
              0,
              101
            ],
            "page_no": 84
          }
        ],
        "self_ref": "#/texts/1318"
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
              "b": 598.5493873908081,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 194.279,
              "t": 607.3508629101564
            },
            "charspan": [
              0,
              14
            ],
            "page_no": 84
          }
        ],
        "self_ref": "#/texts/1319"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md",
    "source_manifest_line_number": 45,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/amendments-to-sttm-and-retail-market-procedures/decision/sttm-procedures-v150.pdf?rev=7f91b14f6cca4ca7bf1e7705ef8362c2&sc_lang=en"
  },
  "content_sha256": "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
  "corpus": "sttm",
  "document_family": "sttm__sttm-procedures-effective-date-3-march-2025",
  "document_family_id": "sttm__sttm-procedures-effective-date-3-march-2025",
  "document_identity": "sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
  "document_title": "##### STTM Procedures Effective date 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-dccf5c023b1c0ea2395683ef.md",
  "heading_path": [
    "Explanatory Note"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93/chunk-dccf5c023b1c0ea2395683ef.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-3-march-2025/sha256-285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93.md"
}
---

Note: That is, the total of variations is assigned to steps, where each step is an absolute GJ quantity.  Thus if the raw variation is -50GJ and the step boundaries are 10GJ, 60GJ and 80GJ then VQ(p,d) = ABS(-50) or 50, GVarU(p,d,1) = min(50,10) = 10, GVarU(p,d,2) = min(50,60) -10 = 40, and GVarU(p,d,3) = min(50,80) -10 -40 = 0.  Thus the total of market schedule variations of 50 is allocated into 3 steps of 10, 40 and 0.  In the variation charge calculation, each of these steps is settled using its factor (GVarF(f) <1) and is applied to the ex ante market price for the hub .
The last step (with f = Maxf) has the otherwise unassigned variation associated with it.
- (b) The GJ variation charge to Trading Participant p for market schedule variations for gas day d is:
<!-- formula-not-decoded -->
