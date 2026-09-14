#!/usr/bin/env python3
import csv, html, os, re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "document-source" / "products.csv"
TDS_DIR = ROOT / "tds"
UG_DIR = ROOT / "usage-guides"
SOP_DIR = ROOT / "sops"

for d in (TDS_DIR, UG_DIR, SOP_DIR):
    d.mkdir(parents=True, exist_ok=True)
    for p in d.glob("*.pdf"):
        p.unlink()

font_regular = "/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"
font_bold = "/usr/share/fonts/truetype/croscore/Arimo-Bold.ttf"
if os.path.exists(font_regular) and os.path.exists(font_bold):
    pdfmetrics.registerFont(TTFont("Arimo", font_regular))
    pdfmetrics.registerFont(TTFont("Arimo-Bold", font_bold))
    FONT = "Arimo"
    FONT_BOLD = "Arimo-Bold"
else:
    FONT = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

RED = colors.HexColor("#C62828")
BLUE = colors.HexColor("#1F4E79")
LIGHT_GRAY = colors.HexColor("#F4F4F4")
DARK = colors.HexColor("#202124")
MID = colors.HexColor("#5F6368")

brand = ParagraphStyle("brand", fontName=FONT_BOLD, fontSize=22, leading=24, textColor=DARK, spaceAfter=5)
title = ParagraphStyle("title", fontName=FONT_BOLD, fontSize=14.5, leading=17, alignment=TA_CENTER, textColor=colors.white)
prod = ParagraphStyle("prod", fontName=FONT_BOLD, fontSize=13, leading=15.5, alignment=TA_CENTER, textColor=DARK, spaceBefore=7, spaceAfter=8)
section = ParagraphStyle("section", fontName=FONT_BOLD, fontSize=10.5, leading=12.5, textColor=DARK, spaceBefore=7, spaceAfter=5)
body = ParagraphStyle("body", fontName=FONT, fontSize=9.2, leading=12.2, textColor=DARK, spaceAfter=5)
small = ParagraphStyle("small", fontName=FONT, fontSize=7.8, leading=10, textColor=MID)
warning = ParagraphStyle("warning", fontName=FONT_BOLD, fontSize=9.2, leading=12, textColor=colors.white)
label = ParagraphStyle("label", fontName=FONT_BOLD, fontSize=8.8, leading=11)
value = ParagraphStyle("value", fontName=FONT, fontSize=8.8, leading=11)


def clean(v):
    return (v or "").strip()


def slug(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def doc_header(story, doc_type, name, sku):
    story.append(Paragraph("Alle's ClinX", brand))
    band = Table([[Paragraph(doc_type, title)]], colWidths=[180 * mm])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE), ("BOX", (0, 0), (-1, -1), 0.7, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(band)
    story.append(Paragraph(html.escape(name), prod))
    info = Table([
        [Paragraph("SKU", label), Paragraph(html.escape(sku), value)],
        [Paragraph("Brand", label), Paragraph("Alle's ClinX", value)],
    ], colWidths=[38 * mm, 142 * mm])
    info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9C9C9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(info)
    story.append(Spacer(1, 5))


def add_warning(story, text):
    t = Table([[Paragraph(html.escape(text), warning)]], colWidths=[180 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), RED), ("BOX", (0, 0), (-1, -1), 0.5, RED),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))


def kv_table(rows):
    data = [[Paragraph(html.escape(k), label), Paragraph(html.escape(v), value)] for k, v in rows if v]
    t = Table(data, colWidths=[52 * mm, 128 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D0D0D0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7.2)
    canvas.setFillColor(MID)
    canvas.drawString(15 * mm, 9 * mm, "Alle's ClinX")
    canvas.drawRightString(195 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(path, metadata_title, subject, keywords, story):
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=15 * mm, leftMargin=15 * mm,
                            topMargin=14 * mm, bottomMargin=15 * mm,
                            title=metadata_title, author="Alle's ClinX Labs", subject=subject)
    def on_page(canvas, d):
        canvas.setTitle(metadata_title)
        canvas.setAuthor("Alle's ClinX Labs")
        canvas.setSubject(subject)
        canvas.setKeywords(keywords)
        footer(canvas, d)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def top_sectors(categories):
    sectors = []
    for part in categories.split(",") if categories else []:
        p = part.strip().split(">")[0].strip()
        if p and p != "Alle's ClinX Products" and p not in sectors:
            sectors.append(p)
    return ", ".join(sectors[:6])

with SOURCE.open(newline="", encoding="utf-8-sig") as f:
    products = list(csv.DictReader(f))

manifest = []
for r in products:
    sku = clean(r["sku"]); name = clean(r["name"])
    chemistry = clean(r["chemistry"]); ph = clean(r["ph"]); shelf = clean(r["shelf_life"])
    pack = clean(r["pack_size"]); ppe = clean(r["ppe"]); avoid = clean(r["avoid"])
    sg = clean(r["specific_gravity"]); foam = clean(r["foam_profile"]); water = clean(r["water_hardness"])
    sector_text = top_sectors(clean(r["categories"]))
    s = slug(name); sku_slug = slug(sku)

    # TDS
    story = []
    doc_header(story, "TECHNICAL DATA SHEET", name, sku)
    story.append(Paragraph("1. Product Overview", section))
    story.append(Paragraph("This publishing-safe TDS provides product identification and non-operational technical information. For handling, hazard classification, PPE, first aid, spill response, storage controls, and any use instructions, refer to the current product label and Safety Data Sheet (SDS).", body))
    story.append(kv_table([
        ("Product / chemistry", chemistry), ("pH", ph), ("Intended sectors", sector_text),
        ("Shelf life", shelf), ("Pack size", pack), ("Specific gravity", sg),
        ("Foam profile", foam), ("Water-hardness note", water),
    ]))
    story.append(Paragraph("2. Safety Reference", section))
    add_warning(story, "SAFETY: Use only under the current product label, SDS, and an approved site procedure. Do not mix chemical products unless an approved controlled document explicitly permits it.")
    if ppe: story.append(Paragraph(f"<b>PPE reference:</b> {html.escape(ppe)}", body))
    if avoid: story.append(Paragraph(f"<b>Known restriction / incompatibility note:</b> {html.escape(avoid)}", body))
    story.append(Paragraph("This document intentionally omits dilution, dosing, mixing, dwell-time, and step-by-step use instructions. Those controls belong in the current label/SDS and trained-site procedures.", small))
    path = TDS_DIR / f"{s}-tds-{sku_slug}.pdf"
    build_pdf(path, f"{name} TDS | Alle's ClinX", f"Technical Data Sheet for {name}, SKU {sku}. Product identity and non-operational technical reference.", f"Alle's ClinX, {name}, {sku}, TDS, technical data sheet", story)
    manifest.append(("TDS", sku, name, path.name))

    # Usage Guide
    story = []
    doc_header(story, "USAGE GUIDE", name, sku)
    story.append(Paragraph("Purpose", section))
    story.append(Paragraph("Quick-reference document for trained staff. It identifies the correct product and the safety checks that must be completed before following the facility's approved work instruction.", body))
    add_warning(story, "BEFORE USE: Confirm the exact product and SKU, read the current label and SDS, and follow the approved site procedure. Do not improvise chemical combinations or use conditions.")
    story.append(Paragraph("Required checks", section))
    checks = [
        "Confirm the container label matches the product name and SKU shown above.",
        "Ensure the current SDS and site-approved work instruction are available.",
        "Use the PPE and engineering controls specified by the current SDS/site risk assessment.",
        "Keep the product in its correctly labelled container and away from incompatible materials.",
        "Stop and escalate if the label, SDS, container condition, or site instruction is unclear.",
    ]
    for c in checks: story.append(Paragraph(f"• {html.escape(c)}", body))
    if shelf: story.append(Paragraph(f"<b>Shelf-life reference:</b> {html.escape(shelf)}", body))
    if pack: story.append(Paragraph(f"<b>Pack-size reference:</b> {html.escape(pack)}", body))
    story.append(Paragraph("Operational quantities, mixing, dilution, contact time, and application steps are intentionally excluded from this publishing-safe guide.", small))
    path = UG_DIR / f"{s}-usage-guide-{sku_slug}.pdf"
    build_pdf(path, f"{name} Usage Guide | Alle's ClinX", f"Safety-focused usage reference for {name}, SKU {sku}.", f"Alle's ClinX, {name}, {sku}, usage guide, safety reference", story)
    manifest.append(("Usage Guide", sku, name, path.name))

    # SOP
    story = []
    doc_header(story, "STANDARD OPERATING PROCEDURE", name, sku)
    story.append(Paragraph("1. Purpose", section))
    story.append(Paragraph("Defines document-control and safety checkpoints for authorized use of this product without replacing the product label, SDS, risk assessment, or site-specific work instruction.", body))
    story.append(Paragraph("2. Scope", section))
    story.append(Paragraph("Applies to trained staff who are authorized by the site to handle this product within an approved task or process.", body))
    story.append(Paragraph("3. Responsibilities", section))
    resp = [["Role", "Responsibility"], ["Site / QA / EHS", "Maintain the approved label, SDS, risk assessment, and controlled work instruction."], ["Supervisor", "Confirm staff authorization, training, and document availability before work begins."], ["Operator", "Follow the current controlled documents exactly and stop work if any information is unclear or inconsistent."]]
    t = Table([[Paragraph(html.escape(str(c)), label if i == 0 else value) for c in row] for i, row in enumerate(resp)], colWidths=[42 * mm, 138 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), BLUE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D0D0D0")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(t)
    story.append(Paragraph("4. Pre-task verification", section))
    for c in checks[:4]: story.append(Paragraph(f"• {html.escape(c)}", body))
    story.append(Paragraph("5. Execution control", section))
    story.append(Paragraph("Carry out the task only under the current approved work instruction and product label. No chemical-use parameters are reproduced in this publishing-safe SOP.", body))
    story.append(Paragraph("6. Completion & records", section))
    story.append(Paragraph("Close and secure the product container, return it to the approved storage location, and complete the site's required task/QA record. Report damaged packaging, exposure, spills, label discrepancies, or document conflicts through the site's incident/deviation process.", body))
    add_warning(story, "STOP WORK if the product identity, SDS, PPE requirements, approved procedure, or container condition is uncertain.")
    path = SOP_DIR / f"{s}-sop-{sku_slug}.pdf"
    build_pdf(path, f"{name} SOP | Alle's ClinX", f"Safety and document-control SOP for {name}, SKU {sku}.", f"Alle's ClinX, {name}, {sku}, SOP, standard operating procedure, safety", story)
    manifest.append(("SOP", sku, name, path.name))

for d, title in ((TDS_DIR, "Technical Data Sheets"), (UG_DIR, "Usage Guides"), (SOP_DIR, "Standard Operating Procedures")):
    (d / "README.md").write_text(f"# {title}\n\nGenerated from `document-source/products.csv`. 35 current Alle's ClinX product documents.\n", encoding="utf-8")

with (ROOT / "document-source" / "generated-manifest.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["document_type", "sku", "product", "filename"]); w.writerows(manifest)

counts = {"tds": len(list(TDS_DIR.glob("*.pdf"))), "usage": len(list(UG_DIR.glob("*.pdf"))), "sops": len(list(SOP_DIR.glob("*.pdf")))}
assert counts == {"tds": 35, "usage": 35, "sops": 35}, counts
print(counts)
