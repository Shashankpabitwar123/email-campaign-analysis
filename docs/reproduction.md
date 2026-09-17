# Reproduce Email Campaign Analysis

## Run the analysis

Use Python 3.12 or newer in an isolated environment. No Windows virtual machine or paid BI license is needed for the Python analysis or public report.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/fetch_data.py
python scripts/analyze.py
python scripts/prepare_excel_data.py
python -m pytest tests -q
python scripts/create_notebook.py
```

On Windows, activate with `.venv\Scripts\activate` instead. The historical provider serves the raw file over HTTP; the downloader checks the exact reviewed SHA-256 and stops if the bytes differ. It does not disable HTTPS certificate checks.

The Excel deliverable can be opened and edited directly. Its authoring script uses the Codex-provided `@oai/artifact-tool` JavaScript package; regenerating that workbook requires that environment. Core analysis, tests, CSV outputs and the notebook use the Python packages above.

The public report is hosted on **GitHub Pages** from the verified `site/` package. See [hosting and deployment](hosting.md) for the publication workflow.

The website's authored analysis is in `web/src/content/dashboard/`. The public report uses an explicitly enabled visitor mode: readers can explore filters and scenarios, but there are no ChatGPT, Publish or editing controls. The publication is built from the included source runtime and package lock. See [hosting and deployment](hosting.md) for source-build and package-verification commands. Preserve `web/AGENTS.md` and runtime integrity metadata.


## Technical evidence

The project demonstrates the following skills:

| Analyst skill | Concrete evidence |
|---|---|
| Business problem definition | Incremental purchase question; explicit recommendation and decision thresholds |
| SQL | Five scripts; CTEs, joins, conditional transformations, aggregation, window ranking, and reconciled reporting grains |
| Data quality | 27 checks across schema, values, denominators and financial reconciliation |
| Experiment analysis | Randomized control, intention-to-treat denominator, Fisher exact tests, multiple-testing correction |
| Statistics | Newcombe intervals, Wilson intervals, 5,000 bootstrap resamples, HC3 regression sensitivity and power planning |
| Excel | Editable budget, XLOOKUP, SUMIFS, validation, break-even calculation and charts |
| Communication | Four report views, short memo, definitions and an honest distinction between evidence and assumptions |
| Reproducibility | Source checksum, fixed random seed, executed notebook, automated tests and version-controlled analysis |


[Return to the project story](../README.md).

## Source and redistribution

The [original dataset description](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html)
does not supply an explicit redistribution license. Raw and cleaned customer
records are therefore excluded from this public repository. The downloader
retrieves the source file and verifies its reviewed checksum; public reporting
files contain derived aggregate results.
