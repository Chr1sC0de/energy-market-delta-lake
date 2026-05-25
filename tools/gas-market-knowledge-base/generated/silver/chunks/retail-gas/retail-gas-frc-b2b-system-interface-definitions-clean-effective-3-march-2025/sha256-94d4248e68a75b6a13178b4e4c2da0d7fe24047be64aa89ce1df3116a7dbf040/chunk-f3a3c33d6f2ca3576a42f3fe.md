---
{
  "chunk_id": "chunk-f3a3c33d6f2ca3576a42f3fe",
  "chunk_ordinal": 869,
  "chunk_text_sha256": "b30799a43f32ea29e9092c60fd506a0dc7d2dd3090587bb72ea0da8f5d04c602",
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
              "b": 264.49371337890625,
              "coord_origin": "BOTTOMLEFT",
              "l": 93.56690216064453,
              "r": 549.273193359375,
              "t": 385.5999450683594
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 258
          }
        ],
        "self_ref": "#/tables/231"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-f3a3c33d6f2ca3576a42f3fe.md",
  "heading_path": [
    "3. List of RoLR transfers (T980)"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040/chunk-f3a3c33d6f2ca3576a42f3fe.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-frc-b2b-system-interface-definitions-clean-effective-3-march-2025/sha256-94d4248e68a75b6a13178b4e4c2da0d7fe24047be64aa89ce1df3116a7dbf040.md"
}
---

mirn, Data Type = Varchar(10). mirn, No Nulls = True. mirn, Primary Key = True. mirn, Comments = MIRN. checksum, Data Type = tinyint. checksum, No Nulls = True. checksum, Primary Key = False. checksum, Comments = MIRN Checksum. frb, Data Type = Varchar(12). frb, No Nulls = True. frb, Primary Key = False. frb, Comments = Failing Retailer Business. e.g ENERGYAUST. rolr, Data Type = Varchar(12). rolr, No Nulls = True. rolr, Primary Key = False. rolr, Comments = Designated retailer. E.g ORIGIN. rolr_date, Data Type = Datetime. rolr_date, No Nulls = True. rolr_date, Primary Key = False. rolr_date, Comments = e.g. yyyy-mm-dd : Date Designated RoLR became FRO
