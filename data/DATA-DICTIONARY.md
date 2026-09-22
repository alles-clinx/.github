# Public data dictionary

This document describes the role of the machine-readable files published under `data/`.

## Curated product data

### `products.json`

Primary structured product dataset. It contains public product identity and reference information together with links to published product documents.

Use this file when an integration needs nested structured data.

### `products.csv`

Tabular representation of the curated product dataset.

Use this file for spreadsheet workflows, imports and simple analytical tooling.

## Document data

### `document-index.json`

Machine-readable index of public PDFs mirrored in the repository. It is intended for document discovery and path resolution.

### `document-register.csv`

Controlled-document register generated from the canonical public library. It records document identity, status, paths and integrity-related metadata.

### `release-manifest.json`

Generated release and integrity manifest. It records the source commit, document counts and per-file metadata such as:

- document type;
- SKU and product where applicable;
- repository path and filename;
- SHA-256 digest;
- file size;
- page count;
- available PDF metadata.

### `legacy-filename-map.csv`

Migration aid mapping previous document filenames to current canonical paths.

## Live-site audit data

### `live-site-inventory.json`

Read-only crawl inventory used to compare public website document discovery with the canonical GitHub library.

### `live-site-document-candidates.csv`

Potential public website documents that require review before they could be considered canonical repository content.

### `site-repository-drift.csv`

Comparison output for repository documents not observed during the live-site crawl.

These audit files are operational discovery artifacts. They do **not** automatically change controlled document status.

## Authority and safety

Structured data improves discoverability and integration convenience. It does not replace the current product label, SDS, TDS, approved SOP, applicable regulation or institutional operating procedure.
