---
{
  "chunk_id": "chunk-820f6ac3c9ec6c3807b02da0",
  "chunk_ordinal": 173,
  "chunk_text_sha256": "7d095c923a8313d2cfddcc1759f7cbff05ed52c14ab04fcc33936605f8a251a5",
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
              "b": 89.10526291015628,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 526.9265600000002,
              "t": 149.27070291015627
            },
            "charspan": [
              0,
              421
            ],
            "page_no": 36
          },
          {
            "bbox": {
              "b": 719.2052629101562,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 526.9323199999994,
              "t": 741.4307029101562
            },
            "charspan": [
              422,
              585
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/467"
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
              "b": 675.2852629101562,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.0559199999996,
              "t": 710.1107029101563
            },
            "charspan": [
              0,
              264
            ],
            "page_no": 37
          }
        ],
        "self_ref": "#/texts/471"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-820f6ac3c9ec6c3807b02da0.md",
  "heading_path": [
    "3.2.7.1.3 Handling of Duplicate Transactions"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-820f6ac3c9ec6c3807b02da0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

On receipt of a transaction, the GRMS will check to see if a transaction with the same transactionID has previously been received. If it has, it will check to see if a receiptID has been assigned to the original transaction, which would indicate that the transaction had been processed and an acknowledgement already dispatched to the  sender.  If  there  is  a  recieptID  for  the  original  transaction,  the  original acknowledgement  will  be  found  (based  on  its  receiptID)  and  resent  with  the duplicate element set to 'Yes' and the date/time updated to the current time.
If no receiptID is logged for the original transaction, this indicates that it is still being internally  processed  and  hence  the  duplicate  will  be  discarded,  as  the  original transaction processing will complete and send an acknowledgement in due course.
