-- Compare like-for-like channel groups against their own randomized control.
-- A rank is descriptive, not a statistically validated targeting policy.
WITH channel_outcomes AS (
    SELECT campaign, prior_channel, count(*) AS customers,
           sum(purchased) AS purchasers, sum(revenue) AS revenue,
           avg(purchased) AS conversion_rate, avg(revenue) AS revenue_per_customer
    FROM customers GROUP BY campaign, prior_channel
), differences AS (
    SELECT t.campaign, t.prior_channel, t.customers, c.customers AS control_customers,
           t.purchasers, c.purchasers AS control_purchasers,
           t.conversion_rate - c.conversion_rate AS conversion_difference,
           t.revenue_per_customer - c.revenue_per_customer AS revenue_difference
    FROM channel_outcomes t
    JOIN channel_outcomes c ON t.prior_channel = c.prior_channel
                          AND c.campaign = 'No email'
    WHERE t.campaign <> 'No email'
)
SELECT *, dense_rank() OVER (PARTITION BY campaign ORDER BY conversion_difference DESC)
          AS exploratory_channel_rank
FROM differences ORDER BY campaign, exploratory_channel_rank;
