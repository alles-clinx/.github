#!/usr/bin/env python3
"""Validate and generate integrity metadata for the Alle's ClinX public document library."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import validate as jsonschema_validate
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COUNTS = {
    "tds": 35,
    "usage-guides": 35,
    "sops": 35,
    "sds": 36,
    "resources": 51,
}

PRODUCT_COLLECTIONS = {
    "tds": {
        "type": "TDS",
        "pages": 2,
        "pattern": re.compile(
            r"^alles-clinx-(?P<product>.+)-technical-data-sheet-(?P<sku>acx-[a-z0-9]+-var)\.pdf$",
            re.I,
        ),
    },
    "usage-guides": {
        "type": "Usage Guide",
        "pages": 1,
        "pattern": re.compile(
            r"^alles-clinx-(?P<product>.+)-usage-guide-(?P<sku>acx-[a-z0-9]+-var)\.pdf$",
            re.I,
        ),
    },
    "sops": {
        "type": "SOP",
        "pages": 2,
        "pattern": re.compile(
            r"^alles-clinx-(?P<product>.+)-standard-operating-procedure-(?P<sku>acx-[a-z0-9]+-var)\.pdf$",
            re.I,
        ),
    },
}

A4_WIDTH = 595.28
A4_HEIGHT = 841.89
A4_TOLERANCE = 4.0

GENERATED_PATHS = [
    ROOT / "checksums.sha256",
    ROOT / "data" / "release-manifest.json",
    ROOT / "data" / "document-register.csv",
    ROOT / "data" / "legacy-filename-map.csv",
    ROOT / "docs" / "status.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def read_manifest() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    path = ROOT / "document-source" / "generated-manifest.csv"
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    by_filename = {row["filename"]: row for row in rows}
    return rows, by_filename


def all_pdf_paths() -> list[Path]:
    paths: list[Path] = []
    for folder in ("tds", "usage-guides", "sops", "sds"):
        paths.extend(sorted((ROOT / folder).glob("*.pdf")))
    paths.extend(sorted((ROOT / "resources").rglob("*.pdf")))
    return sorted(paths, key=rel)


def pdf_info(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path), strict=False)
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ValueError(f"encrypted PDF cannot be opened: {rel(path)}") from exc

    page_sizes: list[tuple[float, float]] = []
    for page in reader.pages:
        box = page.mediabox
        page_sizes.append((float(box.width), float(box.height)))

    metadata = reader.metadata or {}
    title = getattr(metadata, "title", None) or ""
    author = getattr(metadata, "author", None) or ""

    return {
        "pages": len(reader.pages),
        "page_sizes": page_sizes,
        "metadata_title": str(title).strip(),
        "metadata_author": str(author).strip(),
    }


def is_a4(size: tuple[float, float]) -> bool:
    w, h = size
    normal = abs(w - A4_WIDTH) <= A4_TOLERANCE and abs(h - A4_HEIGHT) <= A4_TOLERANCE
    rotated = abs(h - A4_WIDTH) <= A4_TOLERANCE and abs(w - A4_HEIGHT) <= A4_TOLERANCE
    return normal or rotated


def legacy_filename(collection: str, filename: str) -> str:
    if collection == "tds":
        return filename.removeprefix("alles-clinx-").replace(
            "-technical-data-sheet-", "-tds-"
        )
    if collection == "usage-guides":
        return filename.removeprefix("alles-clinx-")
    if collection == "sops":
        return filename.removeprefix("alles-clinx-").replace(
            "-standard-operating-procedure-", "-sop-"
        )
    raise ValueError(collection)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-generated",
        action="store_true",
        help="Write checksums, release manifest, register, legacy map and status page.",
    )
    args = parser.parse_args()

    errors: list[str] = []

    # Validate machine-readable JSON against repository schemas.
    for data_path, schema_path in (
        (ROOT / "data" / "products.json", ROOT / "schema" / "product.schema.json"),
        (
            ROOT / "data" / "document-index.json",
            ROOT / "schema" / "document-index.schema.json",
        ),
    ):
        try:
            jsonschema_validate(instance=load_json(data_path), schema=load_json(schema_path))
        except Exception as exc:
            errors.append(f"schema validation failed for {rel(data_path)}: {exc}")

    manifest_rows, manifest_by_filename = read_manifest()
    if len(manifest_rows) != 105:
        errors.append(f"generated manifest has {len(manifest_rows)} rows; expected 105")

    collection_files: dict[str, list[Path]] = {}
    for collection, expected in EXPECTED_COUNTS.items():
        base = ROOT / collection
        files = sorted(base.rglob("*.pdf")) if collection == "resources" else sorted(base.glob("*.pdf"))
        collection_files[collection] = files
        if len(files) != expected:
            errors.append(f"{collection}: found {len(files)} PDFs; expected {expected}")

    # Ensure canonical product filenames and expected page geometry.
    pdf_cache: dict[str, dict[str, Any]] = {}
    for collection, spec in PRODUCT_COLLECTIONS.items():
        for path in collection_files[collection]:
            if not spec["pattern"].match(path.name):
                errors.append(f"non-canonical filename in {collection}: {path.name}")
            try:
                info = pdf_info(path)
                pdf_cache[rel(path)] = info
                if info["pages"] != spec["pages"]:
                    errors.append(
                        f"{rel(path)}: {info['pages']} pages; expected {spec['pages']}"
                    )
                for page_no, size in enumerate(info["page_sizes"], start=1):
                    if not is_a4(size):
                        errors.append(
                            f"{rel(path)} page {page_no}: not A4 ({size[0]:.2f} x {size[1]:.2f} pt)"
                        )
            except Exception as exc:
                errors.append(f"{rel(path)}: PDF validation failed: {exc}")

    # Parse every remaining public PDF as a basic corruption check.
    for collection in ("sds", "resources"):
        for path in collection_files[collection]:
            key = rel(path)
            if key in pdf_cache:
                continue
            try:
                pdf_cache[key] = pdf_info(path)
            except Exception as exc:
                errors.append(f"{key}: PDF validation failed: {exc}")

    all_pdfs = all_pdf_paths()
    actual_paths = {rel(p) for p in all_pdfs}

    # Validate document index coverage and path integrity.
    document_index = load_json(ROOT / "data" / "document-index.json")
    indexed = document_index.get("documents", [])
    indexed_paths = [d.get("path", "") for d in indexed]
    if document_index.get("total_documents") != len(indexed):
        errors.append("data/document-index.json total_documents does not match entry count")
    if len(indexed_paths) != len(set(indexed_paths)):
        errors.append("data/document-index.json contains duplicate paths")
    missing_from_repo = sorted(set(indexed_paths) - actual_paths)
    missing_from_index = sorted(actual_paths - set(indexed_paths))
    if missing_from_repo:
        errors.append(f"document index references missing files: {missing_from_repo[:5]}")
    if missing_from_index:
        errors.append(f"public PDFs missing from document index: {missing_from_index[:5]}")

    # Validate product document manifest points to the live files.
    for row in manifest_rows:
        collection = {
            "TDS": "tds",
            "Usage Guide": "usage-guides",
            "SOP": "sops",
        }.get(row["document_type"])
        if not collection:
            errors.append(f"unknown manifest document type: {row['document_type']}")
            continue
        path = ROOT / collection / row["filename"]
        if not path.is_file():
            errors.append(f"manifest points to missing file: {rel(path)}")

    # Validate product JSON links to live repository paths.
    products = load_json(ROOT / "data" / "products.json").get("products", [])
    if len(products) != 35:
        errors.append(f"data/products.json has {len(products)} products; expected 35")
    for product in products:
        docs = product.get("documents", {})
        for key in ("tds", "sop", "usage_guide"):
            url = docs.get(key)
            if not url:
                errors.append(f"{product.get('sku')}: missing {key} URL")
                continue
            marker = "/blob/main/"
            if marker not in url:
                errors.append(f"{product.get('sku')}: malformed {key} URL")
                continue
            repo_path = url.split(marker, 1)[1]
            if repo_path not in actual_paths:
                errors.append(f"{product.get('sku')}: {key} URL points to missing {repo_path}")

    if errors:
        print("DOCUMENT LIBRARY QA: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.write_generated:
        source_commit = git_value("rev-parse", "HEAD")
        source_date = git_value("show", "-s", "--format=%cI", "HEAD")
        short_commit = source_commit[:12] if source_commit else "unknown"

        entries: list[dict[str, Any]] = []
        checksum_lines: list[str] = []

        index_by_path = {d["path"]: d for d in indexed}
        for path in all_pdfs:
            rpath = rel(path)
            digest = sha256_file(path)
            checksum_lines.append(f"{digest}  {rpath}")

            indexed_entry = index_by_path.get(rpath, {})
            manifest_entry = manifest_by_filename.get(path.name, {})
            info = pdf_cache[rpath]

            entries.append(
                {
                    "document_type": indexed_entry.get("type", ""),
                    "sku": manifest_entry.get("sku") or None,
                    "product": manifest_entry.get("product") or None,
                    "path": rpath,
                    "filename": path.name,
                    "sha256": digest,
                    "size_bytes": path.stat().st_size,
                    "pages": info["pages"],
                    "metadata_title": info["metadata_title"] or None,
                    "metadata_author": info["metadata_author"] or None,
                }
            )

        counts = {key: len(value) for key, value in collection_files.items()}

        (ROOT / "checksums.sha256").write_text(
            "\n".join(checksum_lines) + "\n", encoding="utf-8"
        )

        release_manifest = {
            "schema_version": 1,
            "source_commit": source_commit or None,
            "source_commit_date": source_date or None,
            "total_documents": len(entries),
            "counts": counts,
            "documents": entries,
        }
        (ROOT / "data" / "release-manifest.json").write_text(
            json.dumps(release_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        register_path = ROOT / "data" / "document-register.csv"
        with register_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "document_type",
                    "sku",
                    "product",
                    "status",
                    "revision",
                    "effective_date",
                    "path",
                    "filename",
                    "sha256",
                    "size_bytes",
                    "pages",
                ],
            )
            writer.writeheader()
            for entry in entries:
                writer.writerow(
                    {
                        "document_type": entry["document_type"],
                        "sku": entry["sku"] or "",
                        "product": entry["product"] or "",
                        "status": "current",
                        "revision": "",
                        "effective_date": "",
                        "path": entry["path"],
                        "filename": entry["filename"],
                        "sha256": entry["sha256"],
                        "size_bytes": entry["size_bytes"],
                        "pages": entry["pages"],
                    }
                )

        legacy_path = ROOT / "data" / "legacy-filename-map.csv"
        with legacy_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "document_type",
                    "sku",
                    "product",
                    "legacy_path",
                    "canonical_path",
                ],
            )
            writer.writeheader()
            for collection, spec in PRODUCT_COLLECTIONS.items():
                for path in collection_files[collection]:
                    row = manifest_by_filename[path.name]
                    writer.writerow(
                        {
                            "document_type": spec["type"],
                            "sku": row["sku"],
                            "product": row["product"],
                            "legacy_path": f"{collection}/{legacy_filename(collection, path.name)}",
                            "canonical_path": rel(path),
                        }
                    )

        (ROOT / "docs").mkdir(exist_ok=True)
        status = f"""# Document Library Status

This page is generated by the repository QA workflow from the canonical document library.

## Current library

| Collection | PDFs |
| --- | ---: |
| Technical Data Sheets | {counts['tds']} |
| Usage Guides | {counts['usage-guides']} |
| Standard Operating Procedures | {counts['sops']} |
| Safety Data Sheets / MSDS | {counts['sds']} |
| Facility Hygiene Resources | {counts['resources']} |
| **Total** | **{len(entries)}** |

## Integrity status

**PASS**

- All indexed PDF paths resolve.
- All public PDFs are represented in the document index.
- All PDFs can be parsed.
- TDS, Usage Guide and SOP filenames match the canonical naming convention.
- Product TDS, Usage Guide and SOP pages are A4.
- Expected page counts are enforced: TDS 2 pages, Usage Guide 1 page, SOP 2 pages.
- Product JSON links resolve to current repository PDFs.
- SHA-256 checksums are published in `checksums.sha256`.

Source commit: `{short_commit}`  
Source commit date: `{source_date or 'unknown'}`
"""
        (ROOT / "docs" / "status.md").write_text(status, encoding="utf-8")

    print("DOCUMENT LIBRARY QA: PASS")
    print(json.dumps({k: len(v) for k, v in collection_files.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
