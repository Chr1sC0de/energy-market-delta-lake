---
{
  "chunk_id": "chunk-1e0f59bd65b19b6ae994ec90",
  "chunk_ordinal": 111,
  "chunk_text_sha256": "fbe6bf3c90f914e1e6d01419cc06a6e40878bf696712154ead7129d577cf9de2",
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
              "b": 154.2186279296875,
              "coord_origin": "BOTTOMLEFT",
              "l": 71.05560302734375,
              "r": 531.6185913085938,
              "t": 549.7727661132812
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 39
          }
        ],
        "self_ref": "#/tables/41"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md",
    "source_manifest_line_number": 30,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/victoria",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/vic/2024/participant-build-pack-1-csv-data-format-specifications-clean.pdf?rev=75d603c0182b4ecbbdfd658be91e2d20&sc_lang=en"
  },
  "content_sha256": "1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143",
  "corpus": "retail_gas",
  "document_family": "retail-gas__participant-build-pack-1-csv-data-format-specifications-clean-effective-30-january-2026",
  "document_family_id": "retail-gas__participant-build-pack-1-csv-data-format-specifications-clean-effective-30-january-2026",
  "document_identity": "retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143",
  "document_title": "##### Participant Build Pack 1 - CSV Data Format Specifications (clean) Effective 30 January 2026",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-1e0f59bd65b19b6ae994ec90.md",
  "heading_path": [
    "6.19 Customer and Site Details from FRB to RoLR (T1010)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143/chunk-1e0f59bd65b19b6ae994ec90.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-participant-build-pack-1-csv-data-format-specifications-clean-effective-79e2cf2040aa/sha256-1cdb596c8d9311ba39c363e90ef0b6f2f1e239872709c9092a0afe63d8ad2143.md"
}
---

NMI, TRANSACTION 1010.Mandatory/ Optional = M. NMI, TRANSACTION 1010.Comment = Must be present. NMI_Checksum, TRANSACTION 1010.Mandatory/ Optional = M. NMI_Checksum, TRANSACTION 1010.Comment = Must be present. Person_Name_Title, TRANSACTION 1010.Mandatory/ Optional = O. Person_Name_Title, TRANSACTION 1010.Comment = Contains customer's title. Required if available.. Person_Name_Given, TRANSACTION 1010.Mandatory/ Optional = O. Person_Name_Given, TRANSACTION 1010.Comment = Contains customer's first name. Required if available.. Person_Name_Family, TRANSACTION 1010.Mandatory/ Optional = O. Person_Name_Family, TRANSACTION 1010.Comment = Contains customer's surname if Business- Name is not populated. Required if available.. Business_Name, TRANSACTION 1010.Mandatory/ Optional = O. Business_Name, TRANSACTION 1010.Comment = Contains company or business name, required if Person_Name_Family is not populated. Required if available.. Business_ABN, TRANSACTION 1010.Mandatory/ Optional = O. Business_ABN, TRANSACTION 1010.Comment = Populate with ABN
