# Analysis plan

## Decision and audience
Help a marketing manager decide whether to repeat either promotional email, and understand the cost assumptions behind that decision. This is an independent retrospective portfolio analysis of Kevin Hillstrom's 2008 public experiment, not a campaign run by the project author.

## Evidence
64,000 rows represent customers who purchased in the preceding 12 months. The source describes random assignment to men's-merchandise email, women's-merchandise email, or no email. These names describe the creative, not customer gender. Follow-up is two weeks. No customer ID, exact campaign dates, opens, delivery logs, unsubscribes, unit costs, or contribution margins are supplied.

This plan was written before running this project's outcome calculations, but the dataset is public and previously analyzed. It is NOT a preregistration or a new confirmatory trial.

## Primary analysis
- Unit: assigned customer. Preserve every valid row, including zero spend and no visit. No conditioning on post-treatment behavior.
- Primary outcome: purchase conversion. Two planned contrasts: each email versus no email.
- Two-sided Fisher exact tests, Holm correction across these two contrasts at family alpha 0.05.
- Absolute conversion differences and relative lifts. Newcombe 95% confidence intervals for individual contrasts and 97.5% intervals for a conservative two-comparison family. Do not interpret intervals as probabilities about the fixed true effect.
- Visit rate and revenue per assigned customer are secondary outcomes. Revenue uses an arm-stratified nonparametric percentile bootstrap (5,000 draws, fixed seed) and a Welch comparison as a sensitivity check.
- A direct comparison between email variants is secondary. Avoid declaring a winner simply because one estimate is larger.

## Diagnostics and robustness
- Validate schema, ranges, categories, missingness, outcome consistency and aggregate reconciliation.
- Check assignment counts against equal allocation; pre-treatment balance uses standardized differences. Diagnostics cannot independently verify the original randomization.
- Preserve identical rows: without a customer ID, matching profiles do not establish duplicate customers.
- Adjust conversion using a linear probability regression with HC3 standard errors and pre-treatment covariates only; use it as a robustness check, not a propensity or individual treatment-effect model.
- Quantify revenue concentration and examine a pooled 99.9th-percentile winsorized sensitivity. Keep the original uncapped estimand primary for revenue.
- Segment analysis by prior purchase channel, recency band and newbie flag is exploratory. Show denominators and uncertainty. It does not establish an optimal targeting policy.

## Planning and communication
- Budget calculator: future contacts × (historical incremental revenue per customer × assumed contribution margin − assumed send cost) − assumed fixed cost.
- Separate historical statistical intervals from future transportability and assumed business inputs. No observed profit or realized ROI claim.
- Follow-up experiment: equal three-arm allocation, conversion primary, a user-selected worthwhile absolute uplift, conservative alpha 0.025 per email comparison and 80% power. Estimate approximate sample size and retain a full two-week outcome window after enrollment.
- Deliver a clear report, reproducible SQL/Python, editable Excel model, analysis notebook, methods and interview guide. A Power BI companion must distinguish prepared files from a report actually opened and validated in Power BI.
