#!/usr/bin/env python3
import csv, html, os, re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "document-source" / "products.csv"
OUT = ROOT / "usage-guides"
OUT.mkdir(parents=True, exist_ok=True)
for p in OUT.glob("*.pdf"):
    p.unlink()

reg = "/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"
bold = "/usr/share/fonts/truetype/croscore/Arimo-Bold.ttf"
if os.path.exists(reg) and os.path.exists(bold):
    pdfmetrics.registerFont(TTFont("Arimo", reg))
    pdfmetrics.registerFont(TTFont("Arimo-Bold", bold))
    FONT, FONT_BOLD = "Arimo", "Arimo-Bold"
else:
    FONT, FONT_BOLD = "Helvetica", "Helvetica-Bold"

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


def clean(v): return (v or "").strip()

def slug(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")

def top_sectors(categories):
    out = []
    for part in categories.split(",") if categories else []:
        p = part.strip().split(">")[0].strip()
        if p and p != "Alle's ClinX Products" and p not in out:
            out.append(p)
    return ", ".join(out[:6])

def concentration_status(name, pack):
    text = f"{name} {pack}".lower()
    if "concentrate" in text:
        return "Concentrate - exact dilution/use concentration must come from the current label or approved controlled instruction."
    if "ready-to-use" in text or "ready to use" in text or "rtu" in text:
        return "Ready-to-use only where the current product label confirms RTU status."
    return "As supplied - verify the current label before deciding whether dilution is required."

def transfer_note(sku):
    if sku.upper() == "ACX-1226-VAR":
        return "Supplied in 5 L pack. If a smaller spray/application bottle is used, it must be compatible, correctly labelled, and controlled under the site's decanting procedure."
    return "If transferred to a secondary container, use only a compatible, correctly labelled container under the site's approved decanting procedure."

def header(story, name, sku):
    story.append(Paragraph("Alle's ClinX", brand))
    band = Table([[Paragraph("USAGE GUIDE", title)]], colWidths=[180*mm])
    band.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE),("BOX",(0,0),(-1,-1),0.7,BLUE),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story.append(band)
    story.append(Paragraph(html.escape(name), prod))
    t = Table([
        [Paragraph("SKU",label),Paragraph(html.escape(sku),value)],
        [Paragraph("Brand",label),Paragraph("Alle's ClinX",value)]], colWidths=[38*mm,142*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),LIGHT_GRAY),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9C9C9")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story.append(t); story.append(Spacer(1,5))

def kv(rows):
    data = [[Paragraph(html.escape(k),label),Paragraph(html.escape(v),value)] for k,v in rows if v]
    t = Table(data,colWidths=[52*mm,128*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),LIGHT_GRAY),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#D0D0D0")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return t

def warn(story, text):
    t=Table([[Paragraph(html.escape(text),warning)]],colWidths=[180*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),RED),("BOX",(0,0),(-1,-1),0.5,RED),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story.append(t); story.append(Spacer(1,6))

def bullet(story, text): story.append(Paragraph(f"• {html.escape(text)}", body))

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont(FONT,7.2); canvas.setFillColor(MID)
    canvas.drawString(15*mm,9*mm,"Alle's ClinX")
    canvas.drawRightString(195*mm,9*mm,f"Page {doc.page}")
    canvas.restoreState()

def build(path, title_meta, subject, keywords, story):
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=14*mm,bottomMargin=15*mm,
                          title=title_meta,author="Alle's ClinX Labs",subject=subject)
    def on_page(canvas,d):
        canvas.setTitle(title_meta); canvas.setAuthor("Alle's ClinX Labs"); canvas.setSubject(subject); canvas.setKeywords(keywords); footer(canvas,d)
    doc.build(story,onFirstPage=on_page,onLaterPages=on_page)

with SOURCE.open(newline="",encoding="utf-8-sig") as f:
    products=list(csv.DictReader(f))

for r in products:
    sku,name=clean(r["sku"]),clean(r["name"])
    chemistry,ph=clean(r["chemistry"]),clean(r["ph"])
    shelf,pack=clean(r["shelf_life"]),clean(r["pack_size"])
    ppe,avoid=clean(r["ppe"]),clean(r["avoid"])
    foam,water=clean(r["foam_profile"]),clean(r["water_hardness"])
    sectors=top_sectors(clean(r["categories"]))
    status=concentration_status(name,pack)

    story=[]; header(story,name,sku)
    story.append(Paragraph("1. Product identification",section))
    story.append(kv([("Product / chemistry",chemistry),("pH",ph),("Pack size",pack),("Use status",status),("Intended sectors",sectors),("Shelf life",shelf)]))
    warn(story,"BEFORE USE: Confirm the exact product and SKU, read the current label and SDS, and follow the approved site procedure. Never guess a dilution, contact time, or chemical combination.")

    story.append(Paragraph("2. Before handling",section))
    for x in [
        "Confirm the container label matches the product name and SKU shown above.",
        "Check that the container is intact, correctly closed, and within its stated shelf-life period.",
        "Make sure the current SDS and the site's approved work instruction are available to the operator.",
        "Use only the PPE, ventilation, and engineering controls specified by the current SDS/site risk assessment."]:
        bullet(story,x)
    if ppe: bullet(story,f"PPE reference from the product data: {ppe}")

    story.append(Paragraph("3. Preparation / dilution control",section))
    bullet(story,status)
    bullet(story,"For concentrates, use only the dilution or use concentration stated on the current label or approved controlled work instruction; this guide does not substitute for that controlled value.")
    bullet(story,"Do not combine with another chemical unless the current label/SDS and an approved site procedure explicitly allow it.")
    bullet(story,transfer_note(sku))

    story.append(Paragraph("4. Surface and compatibility checks",section))
    if avoid: bullet(story,f"Known restriction / incompatibility note: {avoid}")
    else: bullet(story,"Check the current label for excluded surfaces, materials, fabrics, metals, or equipment before use.")
    if water: bullet(story,f"Water-quality reference: {water}")
    if foam: bullet(story,f"Foam-profile reference: {foam}")

    story.append(PageBreak())
    story.append(Paragraph("5. Use-control checks",section))
    for x in [
        "Use only for the task and surface covered by the approved site instruction.",
        "Keep food, open ingredients, and unrelated materials away from the work area where the product label/SDS requires separation.",
        "Do not leave an unlabelled secondary container in service.",
        "Stop work if the appearance, odour, container condition, label, or site instruction is inconsistent with expectations."]:
        bullet(story,x)

    story.append(Paragraph("6. After use",section))
    for x in [
        "Close the original container securely and return it to the approved storage location.",
        "Clean and manage reusable application equipment only under the site's approved procedure.",
        "Record any spill, exposure, damaged pack, incorrect label, or process deviation through the site's incident/deviation process."]:
        bullet(story,x)

    story.append(Paragraph("7. Controlled information",section))
    story.append(Paragraph("Exact dilution ratios, dosing quantities, mixing sequences, contact/dwell times, and other task-specific operating parameters are intentionally not reproduced here. They must be taken from the current product label, SDS where applicable, and the site's approved controlled work instruction so that outdated or unverified values are not propagated.",small))

    fn=f"{slug(name)}-usage-guide-{slug(sku)}.pdf"
    build(OUT/fn,f"{name} Usage Guide | Alle's ClinX",f"Detailed safety-focused usage reference for {name}, SKU {sku}.",f"Alle's ClinX, {name}, {sku}, usage guide, safety reference",story)

(OUT/"README.md").write_text("# Usage Guides\n\nDetailed safety-focused usage references generated from `document-source/products.csv`. Exact dilution ratios, dosing quantities, mixing sequences, and contact/dwell times remain controlled by the current product label, SDS where applicable, and approved site work instructions.\n",encoding="utf-8")
print(f"Generated {len(products)} detailed Usage Guides.")
