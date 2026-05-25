---
{
  "chunk_id": "chunk-8d197b0d4c142c15a53fbbfe",
  "chunk_ordinal": 468,
  "chunk_text_sha256": "96655bfbca7d50fb8a3c035f7b4661d254dc53861c9fb7c4a8d6333cca79c2a6",
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
              "b": 72.21368408203125,
              "coord_origin": "BOTTOMLEFT",
              "l": 67.34481811523438,
              "r": 527.3930053710938,
              "t": 495.7397766113281
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 152
          }
        ],
        "self_ref": "#/tables/153"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md",
    "source_manifest_line_number": 46,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/short-term-trading-market-sttm/procedures-policies-and-guides",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/sttm/policies/sttm-reports-specifications-v190.pdf?rev=ee0167ede9c94105b170ff3edcc2fc99&sc_lang=en"
  },
  "content_sha256": "174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "corpus": "sttm",
  "document_family": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_family_id": "sttm__sttm-reports-specification-effective-date-1-march-2021",
  "document_identity": "sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564",
  "document_title": "##### STTM Reports Specification Effective date 1 March 2021",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-8d197b0d4c142c15a53fbbfe.md",
  "heading_path": [
    "5.5.27. INT735 - NSW ROLR Allocation Quantities"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-8d197b0d4c142c15a53fbbfe.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

Not Null = True. hub_name, Primary Key = False. hub_name, Comment = The name of the hub.. facility_identifier, Not Null = True. facility_identifier, Primary Key = False. facility_identifier, Comment = The unique identifier of the facility. This will always be a Distribution facility.. facility_name, Not Null = True. facility_name, Primary Key = False. facility_name, Comment = The name of the facility. gas_date, Not Null = True. gas_date, Primary Key = True. gas_date, Comment = The gas date that the allocation is applicable for.. crn, Not Null = True. crn, Primary Key = True. crn, Comment = The CRN the allocation relates to.. trn, Not Null = True. trn, Primary Key = True. trn, Comment = The TRN the allocation relates to.. quantity_gj, Not Null = True. quantity_gj, Primary Key = False. quantity_gj, Comment = The last received allocation quantity (GJ) for the TRN and gas date. Note: Gas dates with no allocation quantity available are not
