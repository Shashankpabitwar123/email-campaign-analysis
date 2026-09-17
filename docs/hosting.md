# Hosting the report

The public report is hosted at https://shashankpabitwar123.github.io/email-campaign-analysis/.

GitHub Pages serves the report in `site/`. Charts, customer filters, the budget
calculator, source inspection and downloads work in a browser without a login or
a Power BI license. The data is a fixed historical snapshot, not a live feed.

## Public visitor mode

The public entry point explicitly enables `publicView`. It disables authoring,
ChatGPT prompts, publishing, refresh scheduling and inline editing. The header
contains the report title, analysis date and four navigation tabs. Visitor
filters and budget assumptions remain interactive. Old locally saved title,
layout or chart edits cannot override the published presentation.

This is a source build of the included runtime. Do not replace it with the
standard prebuilt renderer: that renderer does not include this project's
public-view changes. Runtime modifications were scoped and authorized for the
requested standalone portfolio publication; integrity checks remain enabled.

## Rebuild and deploy

1. Follow `web/AGENTS.md` for content, data and protected-runtime boundaries.
2. Use the lockfile with Node 22.12+ or Node 24. With source dependencies installed,
   run `npm run build` in `web`. In the Codex Data environment, use the installed
   Data builder with `--source` to verify and compile this same source runtime.
3. From the repository root, run `python3 scripts/package_site.py`, then
   `python3 scripts/verify_site.py`.
4. Run automated browser checks for the report tabs, customer filters, budget
   scenarios, download links and absence of authoring/ChatGPT controls.
5. Commit and push to `main`. Wait for the Pages workflow to succeed and verify
   the public response against the packaged HTML hash.

`.github/workflows/deploy-pages.yml` verifies the package and deploys `site/`.
The single HTML contains the complete aggregate snapshot. A content-addressed
JSON copy is also included for inspection; its hash must match the snapshot
identity embedded by the compiler. No raw customer records are deployed.

The same HTML works offline. No custom domain, paid hosting or runtime API is
needed. Visual appearance should be reviewed separately by the project owner.
