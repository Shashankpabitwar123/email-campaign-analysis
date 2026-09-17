-- Disjoint cells: every customer contributes to exactly one row.
-- SUMIFS or pivots may safely aggregate these additive numerators and denominators.
SELECT campaign, prior_channel, recency_band, newbie,
       count(*) AS customers,
       sum(purchased) AS purchasers,
       sum(visited) AS visitors,
       round(sum(revenue), 2) AS total_revenue
FROM customers
GROUP BY campaign, prior_channel, recency_band, newbie
ORDER BY campaign, prior_channel, recency_band, newbie;
