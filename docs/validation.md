# Validation record

Validated locally on September 17, 2026.

| Layer | Completed verification |
|---|---|
| Source | Reviewed extract hash matches; all 64,000 records retained |
| Data quality | 27/27 checks passed |
| Python tests | 17 tests passed, including independent count checks, contrast symmetry, bootstrap behavior, budget boundaries and cube reconciliation |
| Notebook | 18 cells executed top-to-bottom; no error outputs; both figures inspected |
| Excel | Five sheets, 65 formulas and two charts; 11 authoring-engine checks passed; exported cached values and formulas reread with openpyxl |
| Excel scenarios | Campaign selection, zero margin and zero contacts produced expected results; defaults restored |
| Web report | Compiled successfully with the pinned Data runtime; all four tabs inspected; segment filter updated chart and table; zero-margin budget case checked |
| Web presentation | Desktop width 1,365px and narrow width 390px inspected; no whole-page horizontal overflow in the results view; source panel and chart image export checked |

The workbook was rendered with the authoring engine and read back from XLSX. It was not interaction-tested in a native Microsoft Excel session. The alternate npm source build was not the publication build tested here.

Power BI CSVs and DAX are a prepared companion kit. A native Power BI report and `.pbix` file were not created or validated. The public interactive website is a separate completed implementation.

Public hosting and repository links are recorded in `project-links.md`. The deployment succeeded with public access, and the uploaded HTML and snapshot were read back with matching hashes. The public GitHub repository's analysis workflow passed on an independent Linux runner. The analysis is a fixed historical snapshot, not live data or a deployed campaign.
