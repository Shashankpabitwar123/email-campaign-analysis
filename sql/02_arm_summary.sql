SELECT campaign, COUNT(*) AS customers, SUM(visited) AS visitors,
       SUM(purchased) AS purchasers, SUM(revenue) AS total_revenue,
       AVG(visited) AS visit_rate, AVG(purchased) AS conversion_rate,
       AVG(revenue) AS revenue_per_customer,
       SUM(revenue)/NULLIF(SUM(purchased),0) AS revenue_per_purchaser,
       VAR_SAMP(revenue) AS revenue_variance
FROM customers GROUP BY campaign ORDER BY campaign;
