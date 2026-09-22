# Alle's ClinX Library — Master Execution Plan

## Locked design rules

- Background: pure white (`#ffffff`) on every Library page.
- Corner radius: maximum 8px, and only where a real UI control/container needs it.
- Category pages: clean index of subcategories.
- Subcategory pages: clean index of articles.
- Article pages: single-column reading layout.
- Article subsections: `#anchors`, not separate pages.
- No decorative dashboard cards, gradients, heavy shadows, or unnecessary divider lines.
- Breadcrumbs remain structural and understated.
- Search is available on category/subcategory indexes.
- Typography and whitespace provide most of the hierarchy.

## Locked URL model

```text
/library/
/library/{category}/
/library/{category}/{subcategory}/
/library/{category}/{subcategory}/{article}/
/library/{category}/{subcategory}/{article}/#{section}
```

## Information architecture

Current master taxonomy:

- **13 categories**
- **107 subcategories**
- Article count is intentionally not locked yet. Articles will be created from search intent and real user questions rather than arbitrary quotas.

## Execution sequence

### Phase 1 — Architecture lock
Status: **in progress / mostly locked**

1. Finalise category names.
2. Finalise subcategory names and slugs.
3. Check for overlap and thin subcategories.
4. Define canonical ownership for topics that could fit more than one category.
5. Freeze v1 URL structure before publishing articles.

Deliverable: `alles-clinx-library-taxonomy-master.json`.

### Phase 2 — Template system
Status: **started**

Use the approved white design system to maintain three templates:

1. `/library/{category}/` — Category index.
2. `/library/{category}/{subcategory}/` — Subcategory/article index.
3. `/library/{category}/{subcategory}/{article}/` — Single-column article.

The current Cleaning Chemistry category and pH subcategory are the visual control samples.

### Phase 3 — Existing-content inventory

Before drafting new articles, map existing Alle's ClinX material into the taxonomy:

- website Learn pages
- support guides
- product pages
- TDS
- SDS
- Usage Guides
- SOPs
- facility-hygiene resources
- Nova/Metricon support material

Each existing asset gets one of four states:

- `reuse`
- `rewrite`
- `supporting-source`
- `do-not-publish-as-article`

This prevents duplicate pages and keyword cannibalisation.

### Phase 4 — Article map

For every subcategory, create article candidates based on:

1. core definitions
2. how-to/search-intent questions
3. troubleshooting questions
4. comparisons
5. selection/decision questions
6. compliance/reference questions where appropriate

Rule: an **article** must answer a complete search intent. Smaller questions become `#anchor` sections inside that article.

### Phase 5 — Priority order

Build the first article clusters where Alle's ClinX already has strong technical authority and documents:

1. Cleaning Chemistry & Product Knowledge
2. Floor & Surface Care
3. Kitchen & Food-Service Hygiene
4. Washroom Hygiene
5. Laundry & Fabric Care
6. Disinfection & Infection Prevention
7. Safety, Compliance & Documentation
8. Hand Hygiene
9. Cleaning & Housekeeping
10. Facility Hygiene Management
11. Cleaning Equipment & Systems
12. Facility & Sector Guides
13. Alle's ClinX Tools & Support

### Phase 6 — Content production

For each article:

1. assign canonical URL
2. define primary question/search intent
3. define H1
4. build section anchors
5. draft from authoritative source material
6. add related internal links
7. connect relevant Alle's ClinX product/document only when contextually useful
8. fact-check
9. publish
10. add to subcategory index

### Phase 7 — Technical SEO

Every published article should include:

- unique `<title>`
- meta description
- canonical URL
- breadcrumb structured data
- Article/WebPage structured data where appropriate
- stable H1
- semantic H2/H3 hierarchy
- descriptive anchor IDs
- internal links to parent subcategory/category
- related article links
- XML sitemap inclusion
- no duplicate indexable article variants

### Phase 8 — QA

Before a category is considered complete:

- all links resolve
- breadcrumbs are correct
- white background is preserved
- mobile layout is clean
- search/filter works
- no duplicate article intents
- no orphan articles
- no unsafe unsupported technical claims
- document links point to current controlled versions

## Immediate build batch

Start with:

```text
/library/cleaning-chemistry/
/library/cleaning-chemistry/chemistry-basics/
/library/cleaning-chemistry/ph-acid-alkaline/
/library/cleaning-chemistry/surfactants/
/library/cleaning-chemistry/disinfectant-actives/
/library/cleaning-chemistry/enzymes/
/library/cleaning-chemistry/bleaches-oxidisers/
/library/cleaning-chemistry/dilution-concentration/
/library/cleaning-chemistry/water-hardness/
/library/cleaning-chemistry/product-selection/
/library/cleaning-chemistry/product-compatibility/
```

Then build the first article map for these 10 subcategories before generating dozens of article pages.

## Build principle

**Structure first → article map second → source mapping third → writing fourth → publication last.**

This prevents the Library from becoming a collection of disconnected SEO pages.