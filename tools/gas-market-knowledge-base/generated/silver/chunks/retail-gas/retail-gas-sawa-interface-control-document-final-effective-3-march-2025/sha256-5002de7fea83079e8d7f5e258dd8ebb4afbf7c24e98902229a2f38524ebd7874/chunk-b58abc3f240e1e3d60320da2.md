---
{
  "chunk_id": "chunk-b58abc3f240e1e3d60320da2",
  "chunk_ordinal": 946,
  "chunk_text_sha256": "7b6259cb471e888f744b6b194ec174e663376a91bb6ff57608fba9db393ad63f",
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
              "b": 519.6939829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.4259999999997,
              "t": 599.0259829101564
            },
            "charspan": [
              0,
              448
            ],
            "page_no": 306
          }
        ],
        "self_ref": "#/texts/3253"
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
              "b": 458.61398291015627,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3059999999998,
              "t": 510.34598291015624
            },
            "charspan": [
              0,
              269
            ],
            "page_no": 306
          }
        ],
        "self_ref": "#/texts/3254"
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
              "b": 355.99398291015626,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3379999999997,
              "t": 449.14598291015625
            },
            "charspan": [
              0,
              547
            ],
            "page_no": 306
          }
        ],
        "self_ref": "#/texts/3255"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b58abc3f240e1e3d60320da2.md",
  "heading_path": [
    "10.10.3.6.1 Applying the surplus into the bid stack"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-b58abc3f240e1e3d60320da2.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

After the end of the gas day, when all the off-market trading is derived and applied, the residual of the trades is derived for each of the swing service provider for the gas day, sub-network, pipeline and type of swing service. The residual is derived as the difference between the total amount of submitted confirmations  by  the  swing  service  provider  and  the  total  amount  of  the applied trades on behalf of this swing service provider.
The residual is apportioned to a number of new bids using the percentage supplied by the swing service provider in the surplus instruction. For each new bid applied into the bid-stack the price nominated by the swing service provider in the surplus instruction is used.
It  is  suggested  that  the  PRIORITY  is  a  unique  number  across  the  swing service provider surplus instruction. If there is duplicate priority the GRMS doesn't guarantee the order in which the quantity instruction will be applied during  the  process.  Currently  the  priority  is  not  used  as  only  percentage allocation  types  are  accepted.  It  is  foreseen  in  the  future  the  market  will require Quantity allocation and therefore the priority will be used to set the order in which the quantity instructions will be applied.
