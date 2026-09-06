# Document Library Import

Upload the three Alle's ClinX document ZIP archives to this folder. The repository workflow automatically extracts them into the public document library and removes the ZIP files after a successful import.

Expected archive families:

- `*Product_Usage_Guides*.zip` → `/usage-guides/`
- `*Product_SOPs*.zip` → `/sops/`
- `*Free_Hygiene_Resources*.zip` → `/resources/`

The import verifies **36 Usage Guide PDFs**, **36 SOP PDFs**, and **51 resource PDFs** (50 operational resources plus the resource-library index) before committing the extracted library.
