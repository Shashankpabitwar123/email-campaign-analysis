# Email Campaign Analysis

**A store wants to know whether promotional emails bring in extra buyers—and which email to send next.**

I explored this using Kevin Hillstrom's public experiment from **2008**, with **64,000 customers**. Customers were randomly split into three groups: an email about men's products, an email about women's products, or no email. Their visits, purchases and spending were tracked for **two weeks**.

**[Explore the live report](https://shashankpabitwar123.github.io/email-campaign-analysis/)** · **[Open the Excel budget model](artifacts/Email_Campaign_Budget.xlsx)**

## Key findings

To compare the groups fairly, these results are shown for every 1,000 customers:

| Group | Roughly how many bought something? |
|---|---:|
| No email | **6 out of 1,000** |
| Men's products email | **13 out of 1,000** |
| Women's products email | **9 out of 1,000** |

Some customers bought even without an email. Compared with that group, the men's email brought in about **7 extra buyers per 1,000 customers**, and the women's email about **3 extra buyers**.

**My recommendation:** make the men's-products email the leading option in a fresh test with today's customers. The data is from 2008, so the result needs to be tested again before spending heavily.

## What I did

I analyzed an existing experiment; I did not send the emails or run the original campaign.

1. **Checked the data** with SQL and Python so the groups and totals could be trusted.
2. **Compared the results** and used statistical tests to assess whether the differences could be explained by chance.
3. **Explored customer groups** using their previous shopping behavior.
4. **Built an Excel budget model and interactive report** to connect the findings to a spending decision.

![Purchase rates in the three experiment groups](artifacts/figures/conversion.png)

The exact purchase rates were **0.57% without email, 1.25% for the men's email and 0.88% for the women's email**. The counts above are rounded for readability. [See the full findings and uncertainty](docs/decision-memo.md).

## Follow the story in the live report

| Report tab | What you can understand or try |
|---|---|
| Results | Understand the experiment and compare extra purchases and revenue |
| Customer segments | Explore whether the pattern differs by previous shopping behavior |
| Budget & next test | Change campaign costs and customer numbers, then see whether the extra sales could cover the costs |
| Methods & downloads | Check the evidence, definitions and calculations, or download the work |

The budget figures are **estimates based on assumptions**, not money I earned or profit observed in this study. For example, the men's email gives an estimated **$2,849 after the modeled costs** with 10,000 contacts, 50% contribution margin, a $0.05 email cost and a $500 fixed campaign cost. Changing those assumptions changes the answer.

## About the data

Each row represents one customer: their past shopping behavior, assigned email group, and visits, purchases and spending during the follow-up. The email names describe the products advertised, not the customers' gender.

Source: [Kevin Hillstrom's MineThatData email experiment, March 2008](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html). This is a historical analysis prepared in September 2026. Customer-level files are excluded from this repository; the project includes aggregate results and a downloader that verifies the original file. Source and redistribution limits are recorded in the [data dictionary](docs/data-dictionary.md) and [reproduction guide](docs/reproduction.md).

## Inspect the work

- **Analysis:** [Executed Python notebook](artifacts/Email_Campaign_Analysis.ipynb) · [SQL queries](sql/) · [Statistical methods](docs/methodology.md)
- **Business decision:** [Decision memo](docs/decision-memo.md) · [Excel workbook](artifacts/Email_Campaign_Budget.xlsx) · [Plan for a new experiment](docs/future-experiment.md)
- **Quality and reproduction:** [Validation record](docs/validation.md) · [Data definitions](docs/data-dictionary.md) · [Run the project](docs/reproduction.md)

A [Power BI companion folder](powerbi/README.md) contains prepared CSVs and DAX; it is an import kit, not a completed Power BI report. The live website above is the completed interactive report.

Built by **Shashank Pabitwar** · SQL, Python, Excel and interactive reporting
