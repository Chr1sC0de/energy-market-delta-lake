---
{
  "chunk_id": "chunk-db89ddcae75dc832c5d181c0",
  "chunk_ordinal": 101,
  "chunk_text_sha256": "1fe4058ddb6ac359c83b0d24b112705028af315240443fe3351ae8710d211b9d",
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
              "b": 150.52878291015622,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 523.3754400000005,
              "t": 212.35086291015625
            },
            "charspan": [
              0,
              458
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/189"
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
              "b": 91.25278291015627,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 517.4197600000002,
              "t": 139.87086291015635
            },
            "charspan": [
              0,
              325
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/190"
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
              "b": 72.05278291015634,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 457.14904,
              "t": 80.71486291015628
            },
            "charspan": [
              0,
              94
            ],
            "page_no": 26
          }
        ],
        "self_ref": "#/texts/191"
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
              "b": 736.0887829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 333.39904,
              "t": 744.7508629101563
            },
            "charspan": [
              0,
              63
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/texts/196"
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
              "b": 455.0187829101563,
              "coord_origin": "BOTTOMLEFT",
              "l": 68.064,
              "r": 529.0397200000003,
              "t": 463.6808629101563
            },
            "charspan": [
              0,
              107
            ],
            "page_no": 27
          }
        ],
        "self_ref": "#/texts/197"
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
  "generated_path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-db89ddcae75dc832c5d181c0.md",
  "heading_path": [
    "2.4. Folder Structure on FTP Server"
  ],
  "path": "generated/silver/chunks/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564/chunk-db89ddcae75dc832c5d181c0.md",
  "schema_version": 1,
  "source_document_markdown_path": "generated/silver/documents/sttm/sttm-sttm-reports-specification-effective-date-1-march-2021/sha256-174cb200d57acaa6551439427a33d1518f88c8c4bc150bc95a97e8821a00c564.md"
}
---

STTM requires Market Participants to retrieve and submit data to AEMO for the functioning of the market. Several mechanisms have been described in the Participant Build Pack and Reports Specifications Document and one of them is FTP. STTM runs an FTP server within IIS and each participant is provided with a folder where the participant deposits files to and retrieves files from. Access to these folders has been controlled by permissions to these folders.
The folders are named according to the scheme ORGnnn for the report directory name where the nnn is the Company_Id of that Organization in AEMO Organisation Register Global (ORG) application. This will make it easier to maintain the application in the event of Organizations changing their names due to acquisition or merger.
Public reports are accessible from the Public folder and this folder is not access controlled.
The folder structure for the FTP site is set up as shown below:
The latest MIS reports are accessed from the ORGnnn directory. When a new report is created, it is put into
