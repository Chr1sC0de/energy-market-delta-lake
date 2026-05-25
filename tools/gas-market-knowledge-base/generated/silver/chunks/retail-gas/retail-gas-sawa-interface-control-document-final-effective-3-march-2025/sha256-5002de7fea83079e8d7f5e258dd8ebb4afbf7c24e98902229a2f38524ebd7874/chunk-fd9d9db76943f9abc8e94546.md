---
{
  "chunk_id": "chunk-fd9d9db76943f9abc8e94546",
  "chunk_ordinal": 197,
  "chunk_text_sha256": "cb259b38354dc42df2d4d01b7a84a7d8d51fb88145172c459d317496ab0acafc",
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
              "b": 579.5739829101564,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.416,
              "t": 645.1359829101564
            },
            "charspan": [
              0,
              318
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/565"
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
              "b": 504.57398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3379999999999,
              "t": 570.1059829101563
            },
            "charspan": [
              0,
              349
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/566"
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
              "b": 457.1710738192472,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3839999999997,
              "t": 495.1059829101563
            },
            "charspan": [
              0,
              213
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/567"
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
              "b": 409.75398291015625,
              "coord_origin": "BOTTOMLEFT",
              "l": 155.9,
              "r": 527.3859999999997,
              "t": 447.71798291015625
            },
            "charspan": [
              0,
              190
            ],
            "page_no": 43
          }
        ],
        "self_ref": "#/texts/568"
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
  "generated_path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-fd9d9db76943f9abc8e94546.md",
  "heading_path": [
    "Security"
  ],
  "path": "generated/silver/chunks/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874/chunk-fd9d9db76943f9abc8e94546.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/retail-gas/retail-gas-sawa-interface-control-document-final-effective-3-march-2025/sha256-5002de7fea83079e8d7f5e258dd8ebb4afbf7c24e98902229a2f38524ebd7874.md"
}
---

The  security of data transactions which are passed between market participants  and  the  GRMS over the internet will  be established using the Virtual Private Network (VPN). A VPN is essentially an encryption tunnel; it  uses  encrypted  IPSEC  connections  at  known  end-points  to  implement transaction security.
A VPN will be established between each individual market participant and the  GRMS.  This  will  allow  for  encryption  across  either  (i)  the  entire communications channel between the market participant's firewall appliance and  the  GRMS  firewall  appliance,  or  (ii)  the  connection  between  a  client machine and GRMS firewall appliance.
Participants will be provided with a username and password to allow access to the FTP server and upon logon shall only be able to access those directories required to submit and receive automatic electronic files.
Each  file  in  the  participant in directory  will  be  further  authenticated  by checking that the sender in the envelope header (or file name) matches the directory the file is found in.
