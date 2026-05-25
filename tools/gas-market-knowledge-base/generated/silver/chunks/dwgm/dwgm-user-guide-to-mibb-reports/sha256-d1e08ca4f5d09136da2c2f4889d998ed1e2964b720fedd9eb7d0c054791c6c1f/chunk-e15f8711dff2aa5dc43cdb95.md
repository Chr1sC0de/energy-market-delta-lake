---
{
  "chunk_id": "chunk-e15f8711dff2aa5dc43cdb95",
  "chunk_ordinal": 428,
  "chunk_text_sha256": "933a404d669fafbfec0a80e6accca3da63d08b60a3927b7f85eb04869859b75d",
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
        "label": "table",
        "parent": {
          "$ref": "#/body"
        },
        "prov": [
          {
            "bbox": {
              "b": 358.60711669921875,
              "coord_origin": "BOTTOMLEFT",
              "l": 42.70158004760742,
              "r": 539.1287231445312,
              "t": 526.7939147949219
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 72
          }
        ],
        "self_ref": "#/tables/112"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md",
    "source_manifest_line_number": 4,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/april-2024-amendment-to-user-guide-to-mibb-reports/user-guide-to-mibb-reports.pdf?rev=b5b659bce66a4808b505db05ecb0ca13&sc_lang=en"
  },
  "content_sha256": "d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "corpus": "dwgm",
  "document_family": "dwgm__user-guide-to-mibb-reports",
  "document_family_id": "dwgm__user-guide-to-mibb-reports",
  "document_identity": "dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f",
  "document_title": "##### User Guide to MIBB Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-e15f8711dff2aa5dc43cdb95.md",
  "heading_path": [
    "Data content"
  ],
  "path": "generated/silver/chunks/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f/chunk-e15f8711dff2aa5dc43cdb95.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/dwgm/dwgm-user-guide-to-mibb-reports/sha256-d1e08ca4f5d09136da2c2f4889d998ed1e2964b720fedd9eb7d0c054791c6c1f.md"
}
---

forecast_date, Data Type = varchar 20. forecast_date, No Nulls = True. forecast_date, Primary Key = True. forecast_date, CQ = N. forecast_date, Comments = gas date of forecast e.g. 30 Jun 2007. version_id, Data Type = integer. version_id, No Nulls = True. version_id, Primary Key = True. version_id, CQ = N. version_id, Comments = Forecast version used to identify which forecast was used in the schedule (reference INT108). ti, Data Type = integer. ti, No Nulls = True. ti, Primary Key = True. ti, CQ = N. ti, Comments = Time interval (1-24). forecast_ demand_gj, Data Type = integer. forecast_ demand_gj, No Nulls = True. forecast_ demand_gj, Primary Key = False. forecast_ demand_gj, CQ = Y. forecast_ demand_gj, Comments = forecast total hourly demand (in GJ/hour) potentially used as input in theMCE. vc_override_gj, Data Type = integer.
