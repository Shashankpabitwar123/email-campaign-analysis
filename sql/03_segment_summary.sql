WITH dimensions AS (
 SELECT *, 'Prior channel' AS dimension, prior_channel AS segment FROM customers
 UNION ALL SELECT *, 'Purchase recency', recency_band FROM customers
 UNION ALL SELECT *, 'Newbie flag', CASE newbie WHEN 1 THEN 'Newbie = 1' ELSE 'Newbie = 0' END FROM customers
)
SELECT dimension, segment, campaign, COUNT(*) AS customers,
       SUM(purchased) AS purchasers, SUM(visited) AS visitors,
       SUM(revenue) AS total_revenue, AVG(purchased) AS conversion_rate,
       AVG(revenue) AS revenue_per_customer
FROM dimensions GROUP BY dimension, segment, campaign
ORDER BY dimension, segment, campaign;
