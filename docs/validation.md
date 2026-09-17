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

The workbook was rendered with the authoring engine and read back from XLSX. It was not interaction-tested in a native Microsoft Excel session. The original report used the pinned renderer; the subsequent public-view revision uses the included source runtime.

Power BI CSVs and DAX are a prepared companion kit. A native Power BI report and `.pbix` file were not created or validated. The public interactive website is a separate completed implementation.

Public hosting and repository links are recorded in `project-links.md`. The deployment succeeded with public access, and the uploaded HTML and snapshot were read back with matching hashes. The public GitHub repository's analysis workflow passed on an independent Linux runner. The analysis is a fixed historical snapshot, not live data or a deployed campaign.

## Public visitor-mode correction — September 17, 2026

The GitHub Pages build previously exposed local authoring controls. The corrected
source build explicitly enables public visitor mode and passes protected-runtime
verification. Automated headless Chromium checks passed at 1365px and 390px:

- Correct title and nonempty content in all four report tabs.
- No Ask ChatGPT, Publish, editing or refresh controls in the public header.
- No ChatGPT/Codex action links or editable text; double-clicking the title keeps
  the report in view mode.
- Segment campaign filter changes the displayed evidence.
- Budget defaults show $2,849 and $1,122; zero margin gives -$1,000 for both
  campaigns; reset restores the defaults.
- Repository and Excel download links retain their expected destinations.
- No browser runtime/console errors, unexpected hosted API dependencies or
  whole-page horizontal overflow in the results view.
- Package hashes match the compiled HTML, runtime manifest and unchanged
  64,000-customer aggregate snapshot.

These checks used the available Playwright runtime because the Browser plugin
was not available. No screenshots or manual visual review were performed for
this revision, at the owner's request. The owner will review the appearance.
