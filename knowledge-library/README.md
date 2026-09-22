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
- `categories/` — WordPress-ready category page controls
- `templates/` — article layout control sample
- `taxonomy/` — canonical taxonomy and URL routing
- `registry/by-category/` — SEO-audited article registry split into 13 category files (317 records total)
- `import/` — WordPress importer test/bootstrap JSON
- `seo/` — word-count and SEO audit
- `plans/` — architecture and execution plans

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
