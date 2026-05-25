---
{
  "chunk_id": "chunk-c78abb50a5a1cc0dabf39eed",
  "chunk_ordinal": 242,
  "chunk_text_sha256": "46979853d2192c741de50fffedcb6b8aee227ebcda14ddf8735738dcf63580a0",
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
              "b": 344.3539829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3659999999996,
              "t": 423.68598291015627
            },
            "charspan": [
              0,
              427
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/texts/885"
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
              "b": 324.55398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 291.89,
              "t": 334.88598291015626
            },
            "charspan": [
              0,
              29
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/texts/886"
      },
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
              "b": 229.023193359375,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.26458740234375,
              "r": 524.9261474609375,
              "t": 298.794189453125
            },
            "charspan": [
              0,
              0
            ],
            "page_no": 55
          }
        ],
        "self_ref": "#/tables/38"
      }
    ],
    "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md",
    "source_manifest_line_number": 37,
    "source_manifest_path": "generated/bronze/source_manifest.jsonl",
    "source_page_url": "https://www.aemo.com.au/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/western-australia",
    "source_url": "https://www.aemo.com.au/-/media/files/gas/retail_markets_and_metering/market-procedures/sa_and_wa/2025/sawa-interface-control-document-v54.pdf?rev=81d1827dbc8d4f78b3277eb532cafa89&sc_lang=en"
  },
  "content_sha256": "5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874",
  "corpus": "retail_gas",
  "document_family": "retail-gas__sawa-interface-control-document-final-effective-3-march-2025",
  "document_family_id": "retail-gas__sawa-interface-control-document-final-effective-3-march-2025",
  "document_identity": "retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874",
  "document_title": "##### SAWA Interface Control Document (Final) Effective 3 March 2025",
  "extraction_settings_sha256": "224426f0963c23223372ca358828992878fbbee913345ed77f33e315ca4cee8a",
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-c78abb50a5a1cc0dabf39eed.md",
  "heading_path": [
    "Participants Push Message to GRMS"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-c78abb50a5a1cc0dabf39eed.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

Low volume participants will create  an  aseXML message file,  with  a  file extension of .tmp and push it to their aseXML inbox on the FTP server. Whilst the file is being created it has the file name suffix .tmp.  Once the file transfer is complete the file will be renamed in one atomic (uninterruptible) operation (rather than a copy and a rename). The file will be renamed to change the file name suffix from .tmp to .xml.
Filename format for file is :
Unique ID, 1 = This should be the aseXML message ID, as defined in the 'Guidelines for Development of A Standard for Energy Transactions in XML (aseXML)'.. File name suffix, 1 = (TMP|XML)
