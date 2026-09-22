# Repository automation scripts

These scripts support the integrity and discoverability of the Alle's ClinX public technical library.

## `validate_document_library.py`

Validates the canonical public document library and selected structured datasets.

Checks include:

- expected collection counts;
- JSON schema validation;
- indexed PDF path coverage;
- PDF readability;
- canonical product-document filenames;
- A4 page geometry for product documents;
- expected TDS, Usage Guide and SOP page counts;
- product-data links to repository documents.

Run validation:

```bash
python scripts/validate_document_library.py
```

Regenerate controlled integrity outputs after a validated document update:

```bash
python scripts/validate_document_library.py --write-generated
```

Generated outputs include `checksums.sha256`, the release manifest, document register, legacy filename map and library status page.

## `discover_live_site_documents.py`

Performs read-only discovery against `allesclinx.com` to compare documents visible on the public website with the canonical GitHub library.

Default run:

```bash
python scripts/discover_live_site_documents.py
```

Optional controls:

```bash
python scripts/discover_live_site_documents.py --max-pages 250 --delay 0.04
```

The script writes live-site inventory and drift-review outputs under `data/` and `docs/`.

## Control boundary

Website discovery does not automatically import or promote documents. A newly discovered file remains a review candidate until it passes controlled review and is intentionally added to the canonical public library.
