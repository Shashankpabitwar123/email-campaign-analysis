-- Preserve source observations. row_id is an extract-local row number, not a customer ID.
CREATE OR REPLACE TABLE customers AS
SELECT row_number() OVER () AS row_id,
       recency::INTEGER AS recency_months, history::DOUBLE AS prior_year_spend,
       history_segment, mens::INTEGER AS bought_mens, womens::INTEGER AS bought_womens,
       CASE WHEN zip_code = 'Surburban' THEN 'Suburban' ELSE zip_code END AS area_type,
       newbie::INTEGER AS newbie, channel AS prior_channel,
       CASE segment WHEN 'No E-Mail' THEN 'No email'
                    WHEN 'Mens E-Mail' THEN 'Men''s merchandise'
                    WHEN 'Womens E-Mail' THEN 'Women''s merchandise' END AS campaign,
       visit::INTEGER AS visited, conversion::INTEGER AS purchased,
       spend::DOUBLE AS revenue,
       CASE WHEN recency <= 3 THEN '1–3 months'
            WHEN recency <= 6 THEN '4–6 months' ELSE '7–12 months' END AS recency_band
FROM raw_customers;
