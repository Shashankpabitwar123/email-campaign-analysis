# Hosting the report

The public report is hosted at https://shashankpabitwar123.github.io/email-campaign-analysis/.

GitHub Pages serves the reviewed static report in `site/`. Its interactive charts,
filters, scenario model and downloads run in the browser without a server or a
school Power BI account. The data is a historical snapshot, not a live feed.
Presentation changes made through the standalone report controls stay in the
visitor's browser; they do not change the public repository or other visitors'
reports.

## Deployment

`.github/workflows/deploy-pages.yml` verifies and deploys the `site/` directory
when its contents change on `main`. It can also be run manually in GitHub Actions.
`scripts/verify_site.py` checks the HTML and snapshot hashes, the complete build
status and the 64,000-customer denominator before publication.

The initial Pages package is the byte-for-byte verified split build previously
used for the project's public report. It retains the existing compiled renderer
and aggregate data. No raw customer-level data is added to the deployment.

## Updating the report

1. Update and validate the authored content under `web/src/content/` and reviewed
   snapshot `web/src/data.json` following `web/AGENTS.md`.
2. Build with the installed Data runtime's `--separate-data` option.
3. Copy the verified `index.html`, named snapshot JSON and `data-app-build.json`
   from that completed build into `site/`, removing any superseded snapshot file.
4. Run `python3 scripts/verify_site.py`, preview `site/` with a local HTTP server,
   and check the affected report views and controls.
5. Commit and push, then wait for the Pages workflow and inspect the live URL.

The site's repository subpath is supported by the relative snapshot URL in the
compiled report. No custom domain, paid hosting service or runtime API is needed.
