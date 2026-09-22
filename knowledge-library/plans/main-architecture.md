# Alle's ClinX Knowledge — Main Page & URL Architecture v1

## Root page

**Canonical URL:** `/library/`  
**Visible page title:** `Knowledge`

The main page should stay deliberately shallow. It exposes the **13 subject categories**, not all 107 subcategories at once. This keeps the root understandable while the category pages perform the next layer of navigation.

The main page search can match category names, category descriptions and subcategory names, but the visible result remains the parent category. A later site-wide search can return individual articles directly.

## Canonical route stack

```text
Level 0  /library/
Level 1  /library/{category}/
Level 2  /library/{category}/{subcategory}/
Level 3  /library/{category}/{subcategory}/{article}/
Level 4  /library/{category}/{subcategory}/{article}/#{section}
```

Example:

```text
/library/
/library/cleaning-chemistry/
/library/cleaning-chemistry/ph-acid-alkaline/
/library/cleaning-chemistry/ph-acid-alkaline/what-is-ph-in-cleaning-chemicals/
/library/cleaning-chemistry/ph-acid-alkaline/what-is-ph-in-cleaning-chemicals/#ph-scale
```

## Counts currently mapped

- Categories: **13**
- Subcategories: **107**
- Planned article universe: **317**
- Article URLs are the next mapping layer and should be created only after duplicate/search-intent review.

> Correction to the earlier planning note: the current taxonomy manifest contains **107 subcategories**, not 99.

## Main-page design rules

- Pure white page background.
- No dashboard/bento layout.
- One large title: `Knowledge`.
- One short description.
- One functional search field.
- One restrained category list.
- Category rows link only to canonical category URLs.
- No full article lists on `/library/`.
- No unnecessary pills, tags, cards, badges or filters.
- 8px radius only on the search field and other genuine controls.

## Slug rules

- Lowercase only.
- Words separated with hyphens.
- Permanent trailing slash on page URLs.
- No years/dates in canonical URLs.
- No `.html` in public routes.
- No SKU in a general knowledge article URL.
- Article slug expresses one independent search intent.
- `#section` is used only for a subsection of the same article.
- Do not create multiple article URLs for synonymous intents.

## Canonical ownership where topics overlap

1. **Product selection**
   - General educational logic: `/library/cleaning-chemistry/product-selection/`
   - Alle's ClinX-specific guidance: `/library/alles-clinx/choosing-alles-clinx-products/`

2. **Cleaning schedules**
   - Task-level housekeeping schedules: `/library/cleaning-housekeeping/cleaning-schedules/`
   - Facility-wide program planning: `/library/facility-hygiene-management/cleaning-plans-schedules/`

3. **Disinfectant chemistry**
   - Active ingredient families: `/library/cleaning-chemistry/disinfectant-actives/`
   - Application/disinfection principles: `/library/disinfection-infection-prevention/disinfectant-chemistry/`

4. **Compatibility**
   - Surface/material care perspective: `/library/floor-surface-care/surface-compatibility/`
   - Chemical/product-selection perspective: `/library/cleaning-chemistry/product-compatibility/`

5. **Product documents**
   - Educational explanations of SDS/TDS/SOPs: `/library/safety-compliance/.../`
   - Current Alle's ClinX document access: `/library/alles-clinx/product-documents/`

## Next execution layer

The next file should be the **317-article route registry**. Every proposed article needs:

```text
article_id
category
category_slug
subcategory
subcategory_slug
article_title
article_slug
canonical_url
primary_intent
purpose = usefulness | SEO | both
existing_source
status
```

That registry becomes the source of truth used to generate:
- subcategory pages,
- article pages,
- breadcrumbs,
- internal links,
- XML sitemaps,
- and future redirects.
