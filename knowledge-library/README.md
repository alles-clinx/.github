# Alle's ClinX Knowledge Library

Working source for the Alle's ClinX public Knowledge Library.

## Current architecture

- `/library/` — Knowledge root
- 13 top-level categories
- 107 subcategories
- 317 planned articles
- article sections use stable `#anchors`

Canonical route model:

```text
/library/
/library/{category}/
/library/{category}/{subcategory}/
/library/{category}/{subcategory}/{article}/
/library/{category}/{subcategory}/{article}/#{section}
```

## Repository layout

- `main/` — WordPress-ready Knowledge root page
- `categories/` — all 13 WordPress-ready category page controls
- `templates/` — article and subcategory layout control samples
- `taxonomy/` — canonical taxonomy and URL routing
- `registry/` — SEO-audited 317-article master registry plus review and QA files
- `import/` — WordPress importer test/bootstrap JSON
- `seo/` — word-count and SEO audit
- `plans/` — architecture and execution plans

## Source of truth

Use these files as the current planning controls:

- `taxonomy/library-route-map.json`
- `taxonomy/library-taxonomy-master.json`
- `registry/article-registry-317-seo-audited-v2.json`
- `seo/word-count-seo-audit.md`

## Design rules

- pure white background
- Inter-first typography
- minimal institutional visual language
- 8px maximum corner radius where controls require it
- restrained hover states
- single-column article reading layout
- no decorative dashboard/bento treatment

## Status

The taxonomy and 317-article registry are planning/source-of-truth assets. The complete 317 article bodies are not yet production-written. WordPress imports should default to `draft` until content QA is complete.
