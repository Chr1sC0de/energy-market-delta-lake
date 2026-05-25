---
{
  "chunk_id": "chunk-54538b677a6c45aa6ba5edc8",
  "chunk_ordinal": 141,
  "chunk_text_sha256": "81f07448128016660bb813b5724866ab64139cdc1c12e442075d198a2a98316e",
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
              "b": 201.27520751953125,
              "coord_origin": "BOTTOMLEFT",
              "l": 52.39088821411133,
              "r": 542.3927001953125,
              "t": 748.0366363525391
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/tables/32"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md",
    "source_manifest_line_number": 14,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/procedures-policies-and-guides/procedures-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/natural_gas_services_bulletin_board/site-content/gbb-documents/guides-and-procedures/guide-to-gas-bulletin-board-reports.pdf?rev=8d79cc57e0fd4faf9f5c92e94b42f86b&sc_lang=en"
  },
  "content_sha256": "aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db",
  "corpus": "gbb",
  "document_family": "gbb__guide-to-gas-bulletin-board-reports",
  "document_family_id": "gbb__guide-to-gas-bulletin-board-reports",
  "document_identity": "gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db",
  "document_title": "##### Guide to Gas Bulletin Board Reports",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-54538b677a6c45aa6ba5edc8.md",
  "heading_path": [
    "4.6.2 Data report format"
  ],
  "path": "generated/silver/chunks/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db/chunk-54538b677a6c45aa6ba5edc8.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/gbb/gbb-guide-to-gas-bulletin-board-reports/sha256-aff88ed883f10349a1f8643b207a016593e977203ee233655337f99f944953db.md"
}
---

CapacityQuantity, Description = Standing capacity quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.. CapacityQuantity, Data type = number(18,3). CapacityQuantity, Example / Allowed values = 32.232 25.5 (if the value is 25.500). FlowDirection, Description = Gas flow direction. Values can be either: Receipt: The flow of gas into the BB storage facility or LNG export Delivery: The flow of gas out of the BB storage facility or LNG import Processed: The flow direction type only used for capacities. For LNG export, it represents the amount of gas that can be processed to a liquefied state on a gas day. For LNG import, it represents the amount of gas that can be received and processed into storage on a gas day. Delivery LNG Storage: The flow direction type only used for capacities. For LNG import, it represents the amount of gas withdrawn from storage for processing to a gaseous state on a gas day. NONE - will be displayed for all other BB facilities and. FlowDirection, Data type = varchar(20).
