# Repository Tools

Alle's ClinX uses repository-native automation to keep the public technical library verifiable and aligned with the live website.

## Document library QA

Workflow: `.github/workflows/document-library-qa.yml`

Validates the controlled GitHub library and refreshes:

- `checksums.sha256`
- `data/release-manifest.json`
- `data/document-register.csv`
- `data/legacy-filename-map.csv`
- `docs/status.md`

The QA checks document counts, index coverage, PDF readability, canonical product-document filenames, A4 geometry for TDS/Usage Guide/SOP documents, expected page counts and product-data links.

## Live site document discovery

Workflow: `.github/workflows/live-site-document-discovery.yml`

Script: `scripts/discover_live_site_documents.py`

This tool fetches the public `allesclinx.com` site, reads public sitemaps when available, crawls same-domain HTML pages, follows document-like links, resolves public PDF destinations and compares them with the canonical GitHub library.

Outputs:

- `data/live-site-inventory.json` — inventory of crawled pages and resolved live document links.
- `data/live-site-document-candidates.csv` — live PDFs not confidently matched to the GitHub library.
- `data/site-repository-drift.csv` — repository PDFs not observed during the crawl.
- `docs/live-site-audit.md` — human-readable discovery summary.

The discovery job runs weekly and can also be started manually from GitHub Actions.

### Controlled-publication boundary

Discovery is intentionally read-only. It never auto-imports a PDF from the website. Candidate documents must be reviewed before they are added to the controlled repository. The crawler records document/page identity and availability; it does not extract operational chemistry-use instructions into its reports.

## Controlled releases

Workflow: `.github/workflows/publish-document-release.yml`

A manually initiated release first validates the library and then packages TDS, Usage Guides, SOPs, SDS/MSDS and facility resources with the integrity manifest and checksums.
