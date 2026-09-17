# Explain the project clearly

## A 45-second answer

“I analyzed a public email experiment with 64,000 customers. The business question was whether sending an email caused extra purchases, and whether the additional revenue could justify the campaign cost. I used SQL to prepare and validate the data, Python to compare the two emails with a no-email control, and Excel to build an editable budget model. The men's email increased purchase conversion by about 0.68 percentage points. I reported confidence intervals and corrected for multiple comparisons. Because the dataset is historical and costs were missing, I recommended a fresh test and kept the budget numbers clearly labeled as scenarios.”

## Walk through the report in three minutes

1. **Results:** explain the no-email control and show purchases / assigned customers. Point to the absolute uplift and confidence intervals.
2. **Revenue:** show why a higher average is insufficient. Explain that zeros stay in the analysis and a few large purchases create uncertainty.
3. **Customer segments:** change one breakdown. Explain why these are hypotheses rather than a proven targeting policy.
4. **Budget:** set margin to zero. The model should show only campaign costs. Restore the default and discuss break-even volume.
5. **Methods:** open a source panel and show the quality checks, reproducible SQL and sensitivity analysis.

## Questions you should be able to answer

**Why include people who never opened or visited?**  
Assignment is randomized; visiting is not. Restricting the analysis to visitors can break the comparability created by randomization. Delivery and opens are not supplied here.

**Why is “0.68 percentage points” different from “0.68%”?**  
Conversion moved from about 0.57% to 1.25%. Subtracting the two percentages gives 0.68 percentage points. The relative increase is about 119%, which can sound large because the baseline is small.

**Why Fisher exact?**  
The outcome is binary and relatively rare. Fisher's exact test directly tests the 2×2 counts. With these sample sizes a large-sample alternative would also be reasonable. I explicitly chose a two-sided test instead of selecting the direction after seeing the result.

**Why adjust for multiple tests?**  
Testing two campaigns creates two chances for a false positive. Holm adjusts the p-values across the planned comparison family. The main displayed intervals use a separate Bonferroni allowance; they are not exact Fisher-test inversions.

**Why bootstrap revenue?**  
Most customers spent nothing, while a few spent a lot. Resampling customers shows how much the mean difference varies under the observed distribution. It retains zero-spend customers. It does not predict how a different future audience will behave.

**Why did you keep duplicate-looking rows?**  
There is no customer ID. Two people can have identical recorded profiles and zero outcomes. Dropping them would silently change the population and possibly bias the results.

**What did the regression add?**  
It checks whether adjusting for recorded pre-treatment characteristics materially changes the assignment effect. HC3 standard errors allow heteroskedasticity. I did not use visits or spending after the email as predictors, and I did not claim an individual prediction model.

**Why not select the best segment immediately?**  
Looking across many noisy segments and picking the largest observed uplift overfits the historical sample. A targeting policy needs held-out randomized evaluation or a new experiment. A difference in statistical significance is not proof of a significant difference between segments.

**How would you productionize it?**  
Create a stable assignment/event model in a warehouse, validate ingestion and outcome windows, schedule tested transformations, track pipeline failures, and agree metric definitions with marketing and finance. Add delivery, unsubscribe, returns and actual cost data. None of those operational integrations is claimed to be running in this portfolio project.

## Learn it before putting it on your resume

Run the analysis once yourself. Explain the five SQL files. Change the workbook assumptions, predict the sign of the result, then check it. Reproduce one rate difference by hand. Read the notebook and explain why the source age limits the recommendation.

Use “analyzed a historical randomized experiment,” not “ran an A/B test for a company.” Use “modeled contribution,” not “generated $2,849 profit.” Your interview value comes from understanding and defending the choices, not just displaying the website.
