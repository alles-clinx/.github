#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import time
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://allesclinx.com/"
HOSTS = {"allesclinx.com", "www.allesclinx.com"}
UA = "AllesClinx-Public-Documentation-Auditor/1.0"
TIMEOUT = 20
SEEDS = ("/", "/sitemap/", "/support/media-documents/", "/shop/", "/quality-compliance/")
SITEMAPS = ("/sitemap_index.xml", "/sitemap.xml", "/wp-sitemap.xml")
SKU_RE = re.compile(r"\bACX-[A-Z0-9]+-VAR\b", re.I)
PDF_RE = re.compile(r"\.pdf(?:$|[?#])", re.I)
DOC_RE = re.compile(
    r"\b(sds|msds|tds|technical data|safety data|usage guide|standard operating|sop|"
    r"resource|report|checklist|register|log|audit|assessment|worksheet|template|pdf)\b",
    re.I,
)
ASSETS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".css", ".js",
          ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".webm", ".mp3", ".zip"}


def normalize(raw: str, base: str = BASE_URL) -> str | None:
    raw = (raw or "").strip()
    if not raw or raw.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    p = urlparse(urljoin(base, raw))
    if p.scheme not in {"http", "https"} or p.hostname not in HOSTS:
        return None
    return urlunparse(("https", "allesclinx.com", p.path or "/", "", p.query, ""))


def probable_html(url: str) -> bool:
    ext = Path(urlparse(url).path).suffix.lower()
    return ext not in ASSETS and ext != ".pdf"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slugish(value: str) -> str:
    value = unquote(value).lower()
    value = re.sub(r"\.pdf$", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def guess_type(text: str) -> str:
    s = text.lower()
    if re.search(r"\b(msds|sds|safety-data|safety data)\b", s):
        return "SDS/MSDS"
    if re.search(r"\b(tds|technical-data|technical data)\b", s):
        return "TDS"
    if re.search(r"\b(standard-operating|standard operating|\bsop\b)\b", s):
        return "SOP"
    if re.search(r"\busage[- ]guide\b", s):
        return "Usage Guide"
    if re.search(r"\b(sustainability|annual|report)\b", s):
        return "Report"
    if re.search(r"\b(resource|checklist|register|log|audit|assessment|worksheet|template)\b", s):
        return "Facility Resource"
    return "Other PDF"


def skus(*values: str) -> list[str]:
    found = set()
    for value in values:
        for sku in SKU_RE.findall(value or ""):
            found.add(sku.upper())
    return sorted(found)


def fetch(session: requests.Session, url: str) -> requests.Response | None:
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        return r
    except requests.RequestException:
        return None


def sitemap_sources(session: requests.Session) -> list[str]:
    found = set()
    robots = fetch(session, urljoin(BASE_URL, "/robots.txt"))
    if robots is not None:
        for line in robots.text.splitlines():
            if line.lower().startswith("sitemap:"):
                n = normalize(line.split(":", 1)[1].strip())
                if n:
                    found.add(n)
    for path in SITEMAPS:
        n = normalize(path)
        if n:
            found.add(n)
    return sorted(found)


def sitemap_pages(session: requests.Session, initial: list[str]) -> set[str]:
    pages = set()
    pending = deque(initial)
    seen = set()
    while pending and len(seen) < 30:
        url = pending.popleft()
        if url in seen:
            continue
        seen.add(url)
        r = fetch(session, url)
        if r is None or not r.content.lstrip().startswith(b"<"):
            continue
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError:
            continue
        root_name = root.tag.rsplit("}", 1)[-1].lower()
        locs = [clean_text(e.text or "") for e in root.iter()
                if e.tag.rsplit("}", 1)[-1].lower() == "loc"]
        if root_name == "sitemapindex":
            for loc in locs:
                n = normalize(loc)
                if n and n not in seen:
                    pending.append(n)
        else:
            for loc in locs:
                n = normalize(loc)
                if n:
                    pages.add(n)
    return pages


def probe(session: requests.Session, url: str) -> dict:
    out = {"final_url": url, "http_status": None, "content_type": None,
           "content_length": None, "is_pdf": bool(PDF_RE.search(url))}
    try:
        r = session.head(url, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code in {403, 405}:
            r = session.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True)
        out["http_status"] = r.status_code
        out["final_url"] = normalize(r.url) or url
        ctype = (r.headers.get("content-type") or "").split(";", 1)[0].strip().lower()
        out["content_type"] = ctype or None
        length = r.headers.get("content-length")
        out["content_length"] = int(length) if length and length.isdigit() else None
        out["is_pdf"] = bool(PDF_RE.search(out["final_url"]) or ctype == "application/pdf")
        r.close()
    except requests.RequestException:
        pass
    return out


def repo_docs() -> list[dict[str, str]]:
    data = json.loads((ROOT / "data" / "document-index.json").read_text(encoding="utf-8"))
    return [{"type": str(x.get("type") or ""), "path": str(x.get("path") or ""),
             "filename": str(x.get("filename") or "")}
            for x in data.get("documents", []) if str(x.get("path") or "").lower().endswith(".pdf")]


def best_match(filename: str, dtype: str, found_skus: list[str], records: list[dict[str, str]]):
    exact = [r for r in records if r["filename"].lower() == filename.lower()]
    if exact:
        return "present-exact", exact[0]["path"], 1.0

    candidates = [r for r in records if r["type"] == dtype] or records
    if found_skus:
        slugged = [s.lower() for s in found_skus]
        sku_matches = [r for r in candidates if any(s in r["filename"].lower() for s in slugged)]
        if len(sku_matches) == 1:
            return "present-by-sku", sku_matches[0]["path"], 0.98
        if sku_matches:
            candidates = sku_matches

    target = slugish(filename)
    best_path = None
    best_score = 0.0
    for record in candidates:
        score = SequenceMatcher(None, target, slugish(record["filename"])).ratio()
        if score > best_score:
            best_score = score
            best_path = record["path"]
    if best_score >= 0.88:
        return "present-similar", best_path, round(best_score, 3)
    return "review-candidate", best_path if best_score >= 0.65 else None, round(best_score, 3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=250)
    ap.add_argument("--delay", type=float, default=0.04)
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    sources = sitemap_sources(session)
    discovered = sitemap_pages(session, sources)
    queue = deque()
    queued = set()
    for path in SEEDS:
        n = normalize(path)
        if n and n not in queued:
            queue.append(n)
            queued.add(n)
    for url in sorted(discovered):
        if probable_html(url) and url not in queued:
            queue.append(url)
            queued.add(url)

    pages = []
    seen = set()
    doc_links = set()
    link_sources = defaultdict(list)
    center_skus = set()
    center_coming_soon = 0

    while queue and len(seen) < args.max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        r = fetch(session, url)
        if r is None:
            pages.append({"url": url, "http_status": None, "title": None, "skus": []})
            continue
        if "html" not in (r.headers.get("content-type") or "").lower():
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        title = clean_text(soup.title.get_text(" ", strip=True) if soup.title else "")
        text = clean_text(soup.get_text(" ", strip=True))
        page_skus = skus(text)
        pages.append({"url": normalize(r.url) or url, "http_status": r.status_code,
                      "title": title or None, "skus": page_skus})
        if "/support/media-documents/" in urlparse(url).path:
            center_skus.update(page_skus)
            center_coming_soon += len(re.findall(r"\bcoming soon\b", text, flags=re.I))

        for a in soup.find_all("a", href=True):
            href = normalize(a.get("href", ""), url)
            if not href:
                continue
            anchor = clean_text(a.get_text(" ", strip=True))
            combined = anchor + " " + href
            if PDF_RE.search(href) or DOC_RE.search(combined):
                doc_links.add(href)
                item = {"source_page": url, "anchor_text": anchor}
                if item not in link_sources[href]:
                    link_sources[href].append(item)
            if probable_html(href) and href not in queued and href not in seen:
                queue.append(href)
                queued.add(href)
        if args.delay:
            time.sleep(args.delay)

    records = repo_docs()
    docs = []
    for candidate in sorted(doc_links):
        p = probe(session, candidate)
        if not p["is_pdf"]:
            continue
        final_url = p["final_url"]
        filename = unquote(Path(urlparse(final_url).path).name) or "document.pdf"
        sources_for_link = link_sources.get(candidate, [])
        anchors = " ".join(x["anchor_text"] for x in sources_for_link)
        source_pages = [x["source_page"] for x in sources_for_link]
        found_skus = skus(filename, final_url, anchors, " ".join(source_pages))
        dtype = guess_type(filename + " " + anchors + " " + final_url)
        status, match, score = best_match(filename, dtype, found_skus, records)
        docs.append({
            "document_type_guess": dtype,
            "status": status,
            "skus": found_skus,
            "filename": filename,
            "url": final_url,
            "http_status": p["http_status"],
            "content_type": p["content_type"],
            "content_length": p["content_length"],
            "repo_match": match,
            "match_score": score,
            "source_pages": sorted(set(source_pages))[:8],
            "anchor_texts": sorted({x["anchor_text"] for x in sources_for_link if x["anchor_text"]})[:8],
        })

    dedup = {}
    for d in docs:
        key = d["url"]
        if key not in dedup:
            dedup[key] = d
        else:
            dedup[key]["source_pages"] = sorted(set(dedup[key]["source_pages"] + d["source_pages"]))[:8]
            dedup[key]["anchor_texts"] = sorted(set(dedup[key]["anchor_texts"] + d["anchor_texts"]))[:8]
    docs = sorted(dedup.values(), key=lambda x: (x["document_type_guess"], x["filename"].lower(), x["url"]))

    candidates = [d for d in docs if d["status"] == "review-candidate"]
    observed_repo = {d["repo_match"] for d in docs if d["repo_match"]}
    repo_not_seen = [r for r in records if r["path"] not in observed_repo]

    inventory = {
        "schema_version": 1,
        "base_url": BASE_URL,
        "sitemap_sources": sources,
        "summary": {
            "pages_crawled": len(pages),
            "site_document_links": len(docs),
            "review_candidates": len(candidates),
            "repo_documents": len(records),
            "repo_documents_not_seen_on_live_site": len(repo_not_seen),
            "document_center_skus_seen": len(center_skus),
            "document_center_coming_soon_mentions": center_coming_soon,
        },
        "pages": sorted(pages, key=lambda x: x["url"]),
        "documents": docs,
    }
    (ROOT / "data" / "live-site-inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    with (ROOT / "data" / "live-site-document-candidates.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["status", "document_type_guess", "skus", "filename", "url",
                  "http_status", "repo_match", "match_score", "source_pages"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for d in candidates:
            w.writerow({
                "status": d["status"],
                "document_type_guess": d["document_type_guess"],
                "skus": ";".join(d["skus"]),
                "filename": d["filename"],
                "url": d["url"],
                "http_status": d["http_status"] if d["http_status"] is not None else "",
                "repo_match": d["repo_match"] or "",
                "match_score": d["match_score"],
                "source_pages": ";".join(d["source_pages"]),
            })

    with (ROOT / "data" / "site-repository-drift.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["type", "path", "filename", "site_visibility"])
        w.writeheader()
        for r in sorted(repo_not_seen, key=lambda x: x["path"]):
            w.writerow({**r, "site_visibility": "not-observed-by-crawler"})

    lines = [
        "# Live Site Document Discovery", "",
        "Read-only comparison of the public Alle's ClinX website with the canonical GitHub library.",
        "Newly found files are not imported automatically; they require controlled review.", "",
        "## Current discovery", "",
        f"- Pages crawled: **{len(pages)}**",
        f"- Live PDF/document links resolved: **{len(docs)}**",
        f"- Candidate PDFs needing repository review: **{len(candidates)}**",
        f"- Repository PDFs: **{len(records)}**",
        f"- Repository PDFs not observed by this crawl: **{len(repo_not_seen)}**",
        f"- Document Center SKUs observed: **{len(center_skus)}**",
        f"- Document Center 'coming soon' mentions observed: **{center_coming_soon}**", "",
        "## Candidate documents", ""
    ]
    if candidates:
        lines += ["| Type guess | File | SKU | Live URL | Closest repository match |",
                  "| --- | --- | --- | --- | --- |"]
        for d in candidates[:50]:
            lines.append(f"| {d['document_type_guess']} | {d['filename']} | {', '.join(d['skus']) or '—'} | {d['url']} | {d['repo_match'] or '—'} |")
    else:
        lines.append("No unmatched live PDF candidates were detected.")
    lines += ["", "## Controls", "",
              "- Crawl scope is restricted to allesclinx.com.",
              "- The report records document/page identity and availability, not operational chemistry-use instructions.",
              "- Live files are never copied into the repository automatically.",
              "- Human review is required before a newly discovered document becomes canonical.",
              "- A repository PDF not observed by this crawl is not automatically considered broken or unpublished.", ""]
    (ROOT / "docs" / "live-site-audit.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(inventory["summary"], indent=2))
    return 0 if pages else 1


if __name__ == "__main__":
    raise SystemExit(main())
