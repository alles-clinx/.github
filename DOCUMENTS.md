# Alle's ClinX Public Document Library

The official Alle's ClinX technical and operational library is maintained as a public, version-controlled mirror for professional users, procurement teams, facility operators and technical reviewers.

## Current public collections

| Collection | Scope | Public PDFs |
| --- | --- | ---: |
| [`sds/`](./sds/) | Safety Data Sheets / MSDS | 36 |
| [`tds/`](./tds/) | Technical Data Sheets | 35 |
| [`sops/`](./sops/) | Product Standard Operating Procedures | 35 |
| [`usage-guides/`](./usage-guides/) | Product Usage Guides | 35 |
| [`resources/`](./resources/) | Facility hygiene checklists, logs, templates and resource index | 51 |

**Current repository total: 192 public PDFs.**

The website remains the primary discovery and canonical product-context layer. GitHub provides the public technical mirror and version history.

## Integrity verification

Every public PDF is covered by the repository integrity system:

- `checksums.sha256` publishes SHA-256 digests for authenticity checks.
- `data/release-manifest.json` records file hashes, sizes, page counts and metadata.
- `data/document-register.csv` provides the current controlled-document register.
- `data/legacy-filename-map.csv` maps retired product-document filenames to their canonical replacements.
- `docs/status.md` reports the latest automated QA result.

The automated QA workflow verifies document counts, path/index consistency, PDF readability, product-document naming, A4 geometry for product documents and current product links.

## Official Alle's ClinX links

- Website: https://allesclinx.com/
- Products: https://allesclinx.com/shop/
- Document Center: https://allesclinx.com/support/media-documents/
- ClinXAi: https://allesclinx.com/clinxai/
- Plus: https://allesclinx.com/plus/
- Support: https://allesclinx.com/support/
- Entity reference: [ENTITY.md](./ENTITY.md)

For product use, compatibility or safety decisions, refer to the current product label and the latest official SDS/TDS and operating procedure.
