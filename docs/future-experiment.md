# A fresh email experiment: proposed protocol

This is a design proposal, not an experiment that has been run.

## Decision

Should a current version of either creative receive a larger campaign budget? Define the minimum contribution that justifies the operational effort before looking at results. Obtain actual sending costs and margin from the business owner.

## Eligibility and assignment

Use currently eligible, contactable customers with the required marketing permission. Choose a stable customer identifier, resolve household/interference concerns, exclude overlapping conflicting campaigns under a documented rule, and randomly assign equally to men's merchandise, women's merchandise or no-email holdout. Merchandise labels describe creatives, not gender-based eligibility.

Record assignment before sending. Preserve assignments if delivery fails. The primary analysis denominator is every eligible randomized customer. Report delivery and missing follow-up separately. If randomization is stratified by past channel or purchase recency, record that design and account for it in inference.

## Measurement contract

| Field or event | Why it is needed |
|---|---|
| stable customer ID, eligibility timestamp | Reproducible population and deduplication |
| experiment ID, assignment, assignment timestamp | Audit randomization and exposure window |
| delivery status and timestamp | Diagnose failures without changing the main denominator |
| purchase ID, purchase time, value, returns | Count unique purchasers and net revenue consistently |
| unsubscribe and complaint events | Customer-experience guardrails |
| campaign variable/fixed cost and contribution margin | Translate response into business economics |
| pre-treatment channel and recency | Balance checks and declared exploratory analysis |

Primary metric: at least one purchase within 14 days after assignment. Secondary metric: net revenue per assigned customer within the same window, with a predeclared returns rule. Guardrails should have business-approved thresholds rather than arbitrary values invented for this portfolio.

## Sample size and stopping

Illustrative baseline: 0.5726%. An absolute 0.3 percentage-point improvement corresponds to about 0.8726% conversion. For 80% power, two-sided alpha 0.025 per email-versus-control comparison, and three equal arms, the normal approximation yields 14,989 customers per arm, or 44,967 total. At 90% power the target is 19,572 per arm, or 58,716 total.

Recalculate using a current baseline and the smallest economically worthwhile effect. If the eligible population is insufficient, change the detectable-effect target or study scope before launch; do not silently accept a less informative test. Reserve time for all recruited customers to complete 14 days of follow-up. No calendar completion date can be estimated without recruitment volume.

Use fixed-horizon analysis. Monitor instrumentation and serious guardrail problems during the test; do not repeatedly test effectiveness and stop at the first small p-value. If early stopping is operationally necessary, design a sequential procedure in advance.

## Analysis and decision

Check allocation, outcome completeness and baseline balance. Estimate each email's absolute conversion difference against holdout; use two-sided tests and Holm adjustment. Report uncertainty for revenue and include zero-spend customers. Investigate missingness with documented sensitivity checks rather than quietly excluding affected customers.

A campaign moves forward only if its business economics and guardrails meet the predeclared decision criteria. A statistically significant purchase increase alone is insufficient. Any segment targeting rule requires separate validation; reserve a holdout or run a new randomized policy test.
