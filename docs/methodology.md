# Methodology and analytical boundaries

## The question and estimand

Estimate the difference in two-week purchase probability, and secondarily revenue per assigned customer, for assignment to each email versus assignment to no email. All 64,000 source rows are retained. This is an intention-to-treat style analysis based on the source's assignment labels; receipt and delivery are unavailable.

The source describes random assignment. A causal interpretation within the historical study additionally assumes that those labels are accurate, outcome measurement is comparable, and one customer's assignment does not materially affect another customer's purchases. This extract cannot independently verify the assignment mechanism or cross-customer interference.

## Data preparation and grain

The raw file contains 12 fields and no customer identifier or event dates. SQL creates an extract-local row key and readable derived labels. The `Surburban` source spelling becomes `Suburban` only in the derived field. The 6,562 rows flagged as exact repeated profiles are retained because the profile fields cannot establish duplicate identity.

The local fact table has one row per source customer record. Campaign summaries have one row per assignment. Segment summaries contain separate, overlapping breakdowns by channel, recency and the source newbie flag; they must not be summed across dimensions. The Excel source cube instead has 54 disjoint campaign × channel × recency × newbie cells, so its counts and revenue are additive.

Twenty-seven data checks verify source shape, missing values, allowed categories, binary outcomes, nonnegative money, purchase/visit/spend consistency, mapping and aggregate reconciliation. They are checks of this extract, not proof of complete or correct business instrumentation.

## Primary inference

Two planned contrasts for this retrospective analysis: men's email versus no email; women's email versus no email. The primary outcome is `purchasers / assigned customers`.

- Two-sided Fisher exact tests on the 2×2 purchase tables.
- Holm adjustment across those two p-values at family alpha 0.05.
- Newcombe score-based intervals for the difference in two independent proportions. Individual 95% intervals are retained in the data. The main report displays individual 97.5% intervals with a Bonferroni allowance across two contrasts. Newcombe intervals are approximate and are not obtained by inverting Fisher's exact test.
- Wilson intervals describe each arm's conversion rate. Separate arm-interval overlap is not used to test a difference.

The primary absolute differences are 0.006805 and 0.003111, or 0.6805 and 0.3111 percentage points. Relative changes are also available, but the report leads with absolute change because the baseline rate is small.

## Revenue inference

Revenue per customer includes non-buyers with zero spending. Each arm is independently resampled with replacement 5,000 times using seed 20260917. The bootstrap is calculated by multinomial counts over unique dollar values, which is equivalent to an empirical customer bootstrap. Differences use the corresponding independently generated arm means. The same control bootstrap vector is shared across contrasts, preserving their common-control dependence.

The 2.5th and 97.5th percentiles form individual 95% intervals. Welch tests are supplied as secondary reference checks, not additional primary discoveries. Heavy tails, a small number of purchases and finite bootstrap draws limit precision; these intervals do not solve uncertainty about a future market.

## Diagnostics and sensitivity

- **Allocation:** chi-square goodness-of-fit against the stated equal allocation; p=0.9037. This fails to reveal an allocation-count problem but does not validate randomization.
- **Baseline balance:** standardized mean differences for pre-treatment spending, recency, purchase flags, channels and area types; maximum absolute SMD 0.0137. Standardization uses the pooled group variance, and very small SMDs do not guarantee no unmeasured imbalance.
- **Regression sensitivity:** linear probability model with HC3 robust standard errors. Predictors include assignment, log historical spending, recency, pre-treatment purchase flags and categorical channel/area indicators. Visits, post-email spending and conversion are not used as predictors. Adjusted effects remain close to the simple differences. This is an inference sensitivity model, not a production prediction model.
- **Extreme spend:** cap spending at the pooled 99.9th percentile ($243.66049) only for sensitivity. The cap changes the outcome and is not used in the primary revenue estimate. The top 64 spenders account for 34.86% of total observed revenue.
- **Direct creative comparison and segments:** secondary/exploratory. Segment intervals are individual 95% and not multiplicity-adjusted. No formal interaction claim, optimal audience or out-of-sample targeting performance is asserted.

## Economics and future-test planning

Costs, margin and contact volume are editable assumptions, clearly separated from historical estimates. The budget interval propagates only historical effect uncertainty through fixed business inputs. It is neither a forecast interval nor realized profit.

Sample-size planning uses Cohen's h from the historical control conversion rate and a chosen absolute uplift. `NormalIndPower` solves a two-sided, equal-arm normal approximation at alpha 0.025 per email-versus-control comparison. Reported power applies to each planned comparison under its assumed effect, not the joint probability of detecting both campaigns. Required arm sizes are rounded up and multiplied by three. There is no allowance for missing follow-up; a real test should address this explicitly.

## Reproducibility and references

Source SHA-256: `0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece`.

- [Original dataset description](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html)
- [Statsmodels proportion difference intervals](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html)
- [Statsmodels power analysis](https://www.statsmodels.org/stable/generated/statsmodels.stats.power.NormalIndPower.html)
- [SciPy Fisher exact test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html)

This project's analysis plan is retrospective. The original experiment and publicly available analyses predate this work. There is no claim of preregistration, new data collection or realized commercial impact.
