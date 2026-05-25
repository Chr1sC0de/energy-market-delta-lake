---
{
  "chunk_id": "chunk-2a1746f4bef86c4228ddff7b",
  "chunk_ordinal": 878,
  "chunk_text_sha256": "a396f0d6229a0b2122c19b7cbc3cdf474977b4b0f27359608bd9ed5fa90a7afd",
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
              "b": 73.4508056640625,
              "coord_origin": "BOTTOMLEFT",
              "l": 92.20668029785156,
              "r": 547.9275512695312,
              "t": 506.6854553222656
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 261
          }
        ],
        "self_ref": "#/tables/235"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md",
    "source_manifest_line_number": 26,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/sa_and_wa/2025/frc-b2b-system-interface-definitions-v53-clean.pdf?rev=c312fd435a0b46d4ac08cc4b56c74493&sc_lang=en"
  },
  "content_sha256": "94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040",
  "corpus": "retail_gas",
  "document_family": "retail-gas__frc-b2b-system-interface-definitions-clean-effective-3-march-2025",
  "document_family_id": "retail-gas__frc-b2b-system-interface-definitions-clean-effective-3-march-2025",
  "document_identity": "retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040",
  "document_title": "##### FRC B2B System Interface Definitions (Clean) Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-2a1746f4bef86c4228ddff7b.md",
  "heading_path": [
    "6. Customer and Site Details from FRB to RoLR (T1010)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-2a1746f4bef86c4228ddff7b.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

NMI, Mandatory Optional = M. NMI, / = . NMI, Comment = Must be present. NMI_Checksum, Mandatory Optional = M. NMI_Checksum, / = . NMI_Checksum, Comment = Must be present. Person_Name_Title, Mandatory Optional = O. Person_Name_Title, / = . Person_Name_Title, Comment = Contains customer's title . Required if available. Person_Name_Given, Mandatory Optional = O. Person_Name_Given, / = . Person_Name_Given, Comment = Contains customer's first name . Required if available. Person_Name_Family, Mandatory Optional = O. Person_Name_Family, / = . Person_Name_Family, Comment = Contains customer's surname if Business -Name is not populated. Required if available. Business_Name, Mandatory Optional = O. Business_Name, / = . Business_Name, Comment = Contains company or business name, required if Person_Name_Family is not populated. Required if available. Business_ABN, Mandatory Optional = O. Business_ABN, / = . Business_ABN, Comment = Populate with ABN if customer is a Business. Required if available. Average Daily
