---
{
  "chunk_id": "chunk-e07a93b3afb1f987dbc46b6f",
  "chunk_ordinal": 276,
  "chunk_text_sha256": "37806ddb75e325f1994caa853e351f663af24092956db7cf70f92384982c0564",
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
        "label": "formula",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 725.0174582692723,
              "coord_origin": "BOTTOMLEFT",
              "l": 178.58,
              "r": 469.42144,
              "t": 745.4708629101564
            },
            "charspan": [
              0,
              101
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1030"
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
              "b": 621.7396293189961,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 524.8209999999999,
              "t": 716.6919829101563
            },
            "charspan": [
              0,
              773
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1031"
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
              "b": 578.539629318996,
              "coord_origin": "BOTTOMLEFT",
              "l": 131.9,
              "r": 527.2610000000002,
              "t": 611.4519829101563
            },
            "charspan": [
              0,
              238
            ],
            "page_no": 71
          }
        ],
        "self_ref": "#/texts/1032"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-e07a93b3afb1f987dbc46b6f.md",
  "heading_path": [
    "10.5.3. Allocation to steps -Percentage method"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400/chunk-e07a93b3afb1f987dbc46b6f.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-procedures-effective-date-12-january-2023/sha256-ba25a7381506ae4e39db46c38dd7f7df25e240b5689749627a4a426340328400.md"
}
---

<!-- formula-not-decoded -->
Note : This equation states that if there is no variation then there is no variation charge .  However, if there is a variation, then we calculate the per GJ cost of the total variation charge .  If this charge rate is greater than the amount by which the maximum market price exceeds the ex ante market price then the raw variation charge rate is capped at the amount by which the maximum price exceeds the ex ante market price .  The final rate is multiplied by the variation quantity.  This approach effectively caps the average charge applied to be no greater than the applicable maximum market price less the ex ante market price .  The maximum price allowed in the ex ante market for gas day d is MAXP(d) (which will either be MPC, or APC if prices are administered).
This ensures that a Trading Participant who traded its MSV quantity at the ex ante market price will never have a variation charge which would bring its total $/GJ payment for that gas to exceed the applicable maximum price in the market.
