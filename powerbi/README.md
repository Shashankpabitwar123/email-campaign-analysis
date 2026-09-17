# Power BI companion kit

**Status: prepared import files and DAX; no native report has been created or validated for this project.** The complete interactive report is the separately published website. The school session was available earlier, but native Safari controls and screenshots became unavailable while attempting the new report. No existing Power BI report was changed.

The included CSV files contain derived aggregates only. They can be used in Power BI Service on a Mac, subject to the account's available modeling features and tenant settings. The [Microsoft service tutorial](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-get-started) describes web report creation. The [quick report guide](https://learn.microsoft.com/en-in/power-bi/create-reports/service-quick-create-report) also describes pasting data.

## Tables and relationships

| File | Grain and use |
|---|---|
| FactCampaign.csv | 54 disjoint campaign × prior-channel × recency × newbie cells; additive counts and revenue |
| DimCampaign.csv | Three assignment labels; one-to-many relationship to FactCampaign |
| CampaignEffects.csv | Two whole-population email-versus-control comparisons with Python-derived uncertainty |
| SampleSizePlan.csv | Eight proposed test-size scenarios |

Connect DimCampaign[campaign] to FactCampaign[campaign] with a single-direction one-to-many relationship. Use the dimension's campaign label in slicers and visuals. Keep CampaignEffects and SampleSizePlan disconnected on dedicated pages, so whole-population intervals cannot be mistaken for recalculated segment intervals.

## Suggested report pages

1. **Campaign results:** cards for total customers, purchasers and revenue; bar chart by assignment for Purchase Conversion; table for Incremental Revenue per Customer. Use measures from Measures.dax rather than average-of-averages or sums of percentages.
2. **Customer segments:** channel and recency slicers, campaign dimension columns, Customers, Purchasers, Purchase Conversion and Conversion Uplift pp. Label exploratory. Preserve channel/recency filters when finding the no-email baseline.
3. **Evidence and planning:** whole-population effect table, confidence bounds, adjusted p-values, sample-size table and source/method text. Do not allow FactCampaign segment slicers to imply that these stored interval values have changed.

## Validation checklist for a native implementation

- Total customers 64,000, purchasers 578, revenue $67,258.13.
- No-email conversion 0.5726%, men's email 1.2531%, women's email 0.8837%.
- Whole-population men's uplift 0.6805 percentage points; women's uplift 0.3111 points.
- Channel-filtered control denominators change with the channel, while campaign filters do not hide the control calculation.
- CampaignEffects remains explicitly labeled whole-population. Stored confidence bounds must not be presented as dynamic subgroup inference.
- Test filters, tooltips, totals and reset behavior in Power BI before adding this implementation to a resume.

The native report kit supplements the finished analysis. A `.pbix` file or school-account report link is not included because neither was created and checked in this session.
