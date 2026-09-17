# Decision memo: which email deserves the next test?

**Audience:** a marketing manager deciding whether to invest in another campaign.  
**Recommendation:** use the men's-merchandise creative as the lead candidate in a fresh, controlled experiment. Keep a no-email holdout and measure purchases and revenue across all assigned customers.

## Why this is the recommendation

The historical no-email group converted at 0.57%, compared with 1.25% for the men's email and 0.88% for the women's email. The absolute increases versus control are 0.68 and 0.31 percentage points. Both pass the pre-specified-for-this-reanalysis two-comparison procedure: two-sided Fisher exact tests followed by Holm adjustment.

| Historical effect versus no email | Men's email | Women's email |
|---|---:|---:|
| Additional purchases / 1,000 assigned | 6.81 | 3.11 |
| Conversion uplift | +0.68 pp | +0.31 pp |
| Multiplicity-aware conversion interval | +0.48 to +0.89 pp | +0.13 to +0.50 pp |
| Additional revenue / assigned customer | $0.77 | $0.42 |
| Individual 95% bootstrap revenue interval | $0.49 to $1.06 | $0.16 to $0.68 |

The conversion intervals are individual 97.5% Newcombe intervals used to provide approximately at least 95% coverage across the two comparisons. Revenue is a secondary outcome and its intervals are not adjusted for a broader family of secondary tests.

The direct men's-versus-women's comparison is secondary. It estimates 0.37 percentage points higher conversion for the men's email, with an individual 95% interval of 0.17 to 0.57 points. That supports using it as the lead candidate; it does not establish that it is best for every current customer segment.

## What the budget model says

At **10,000 contacts**, **50% contribution margin**, **$0.05 per email**, and **$500 fixed campaign cost**:

| Scenario | Point estimate | Range from historical revenue uncertainty |
|---|---:|---:|
| Men's email modeled contribution | $2,849 | $1,462 to $4,324 |
| Women's email modeled contribution | $1,122 | -$190 to $2,397 |

The formula is `contacts × (incremental revenue per customer × margin − email cost) − fixed cost`. The model treats the email cost as a cost per assigned recipient because delivery counts are unavailable. Its ranges vary only the historical revenue effect. They exclude uncertainty in costs, margin, current response and the transfer from 2008 to today.

## What could change the decision

- **Current response:** this is a 2008 dataset. Re-estimate the baseline and incremental effect on a current audience.
- **Business economics:** real costs, returns and contribution margin may make a statistically positive campaign unattractive.
- **Customer harm:** delivery, opt-outs and complaints were not supplied. A future campaign must measure them as guardrails.
- **Revenue instability:** 64 customers generated 34.86% of observed spending. The bootstrap and capped-spend sensitivity help reveal this uncertainty; they do not remove it.

## Next action

Run a three-arm test of the current men's creative, women's creative and a no-email holdout. Under the historical 0.57% baseline, detecting an absolute 0.3-point uplift with 80% power requires approximately **14,989 customers per arm** under the stated normal-approximation assumptions. Refresh the baseline, worthwhile effect and recruitment feasibility before using this target.

Do not immediately target or suppress individual customers using the exploratory segment ranks. Those ranks were estimated and inspected on the same historical sample. Validate a proposed targeting rule on new or held-out randomized data first.

Source: [Hillstrom's original challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html). All numeric findings above are calculated by the scripts and notebook in this repository.
