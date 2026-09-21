# Alle's ClinX Tools & Systems

This page is the public index of Alle's ClinX digital tools, planning systems and repository automation.

The customer-facing tools come first. Repository maintenance automation is listed separately so technical controls remain transparent without making raw audit output the focus of the public library.

## Customer-facing digital tools

### ClinXAi

[ClinXAi](https://allesclinx.com/clinxai/) is the umbrella for Alle's ClinX digital intelligence tools.

| Tool | Status | Purpose |
| --- | --- | --- |
| [Nova](https://allesclinx.com/about-nova/) | Available | AI assistant for Alle's ClinX product, documentation and policy questions |
| [Metricon](https://allesclinx.com/metricon/) | Available | Browser-based procurement, application, chemistry and risk calculators |
| CheckMate | Coming soon | Compliance and document-review tooling |
| Lens | Coming soon | Analytics and pattern-insight tooling |
| Atlas | Coming soon | Mapping, tracking and regional-risk tooling |

The live ClinXAi page is the authority for availability status.

### Metricon calculators

Metricon currently exposes calculators across procurement, finance, application, chemistry and risk. The live website remains the authoritative tool directory.

**Procurement & finance:** Total Cost of Ownership (TCO), TCO Alternate, Economic Order Quantity (EOQ), Should-Cost Model, Supplier Preferencing, ROI, Contract Risk Scorer, Kraljic Matrix, NPV, Cost Per Invoice, and MRO Savings.

**Application & planning:** Dilution Calculator, Cost Per Use, Usage / Stock Runway, Coverage, and Dosage.

**Chemistry & lab:** pH, Molarity, Concentration, Specific Gravity, Percent Purity, and Dilution Series.

**Risk & supplier analysis:** Currency Exposure, Disruption Cost, Spend Concentration / HHI, Supplier Health Radar, and Single-Source Risk.

Open the current directory at [Metricon](https://allesclinx.com/metricon/) or the [site map](https://allesclinx.com/sitemap/).

### Alle's ClinX Plus

| Tool / system | Purpose |
| --- | --- |
| [Alle's ClinX Plus](https://allesclinx.com/plus/) | Recurring institutional supply and facility planning |
| [Supply Planner](https://allesclinx.com/plus/supply-planner/) | Supply-cycle planning |
| [Hygiene Passport](https://allesclinx.com/plus/hygiene-passport/) | Connected supply and document record |
| [Facility Tools](https://allesclinx.com/plus/facility-tools/) | Facility-oriented planning and operational resources |

## Repository automation

These tools maintain the public technical repository. They are supporting controls rather than customer-facing products.

| Repository tool | Function |
| --- | --- |
| Import Document Library | Replaces an approved document category from release ZIPs and verifies expected counts |
| Document Library QA | Validates counts, indexes, PDF readability, canonical filenames, page geometry and product links |
| Live Site Document Discovery | Compares public website documents with the canonical GitHub library and flags review candidates |
| Controlled Document Release | Validates and packages a versioned GitHub Release with manifests and checksums |
| Integrity Metadata Generator | Publishes SHA-256 checksums, release manifest, document register and legacy filename map |

Detailed implementation notes remain in [docs/TOOLS.md](./docs/TOOLS.md).

## Publication boundary

The live-site discovery system is intentionally read-only. It does not automatically publish documents found on the website. Candidate files require controlled review before they become part of the canonical GitHub library.

Raw crawler reports and drift files remain available for technical review under docs/ and data/, but they are intentionally not promoted in the main repository overview.
