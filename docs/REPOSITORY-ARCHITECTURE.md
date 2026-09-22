# Repository architecture

The Alle's ClinX `.github` repository currently serves two public roles:

1. the GitHub organization profile; and
2. the canonical public technical-information repository.

The structure is intentionally explicit so each area can later be separated into a dedicated repository if scale or maintenance needs justify it.

## Public profile

- `profile/` — organization profile content and assets.
- `README.md` — repository-level overview.

## Controlled document library

- `sds/` — Safety Data Sheets / MSDS.
- `tds/` — Technical Data Sheets.
- `sops/` — product Standard Operating Procedures.
- `usage-guides/` — product Usage Guides.
- `resources/` — facility hygiene templates, logs, checklists and related resources.
- `DOCUMENTS.md` — human-readable document index.
- `checksums.sha256` — published SHA-256 integrity list.

## Public structured data

- `data/` — curated and generated machine-readable datasets.
- `schema/` — JSON schemas used to validate selected public datasets.
- `organization.json` — machine-readable organization identity.

## Automation and QA

- `scripts/validate_document_library.py` — validates canonical document-library structure and can regenerate integrity metadata.
- `scripts/discover_live_site_documents.py` — performs read-only discovery against the public Alle's ClinX website and reports possible site/repository drift.
- `.github/workflows/` — repository automation and validation workflows.

## Governance

- `PUBLIC-DATA.md` — public/private data boundary.
- `CONTRIBUTING.md` — contribution rules.
- `SECURITY.md` — responsible disclosure guidance.
- `SUPPORT.md` — support channels.
- `CHANGELOG.md` — material changes to the public information layer.

## Future repository split

If the organization grows, the cleanest separation would be:

- a **public-data** repository for structured product/document metadata and schemas;
- a **document-library** repository for controlled PDFs, manifests and integrity controls;
- a **tooling** repository for reusable validation and discovery code.

No split is required simply for appearance. A separate repository should be created only when the component has an independent maintenance lifecycle, user audience or release model.
