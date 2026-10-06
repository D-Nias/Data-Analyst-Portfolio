-- Import data/online_shoppers_intention.csv into SQLite as sessions.
-- Convert Revenue to 1 for TRUE and 0 for FALSE during import.
-- Keep all source rows; identical feature vectors are not proven duplicates.

SELECT COUNT(*) AS sessions,
       SUM(Revenue) AS purchasing_sessions,
       ROUND(100.0 * AVG(Revenue), 2) AS purchase_rate_pct
FROM sessions;

SELECT VisitorType,
       COUNT(*) AS sessions,
       SUM(Revenue) AS purchasing_sessions,
       ROUND(100.0 * AVG(Revenue), 2) AS purchase_rate_pct
FROM sessions
GROUP BY VisitorType
ORDER BY sessions DESC;

SELECT CASE WHEN ProductRelated <= 5 THEN '0-5'
            WHEN ProductRelated <= 20 THEN '6-20'
            WHEN ProductRelated <= 50 THEN '21-50'
            WHEN ProductRelated <= 100 THEN '51-100'
            ELSE '101+' END AS product_page_band,
       COUNT(*) AS sessions,
       SUM(Revenue) AS purchasing_sessions,
       ROUND(100.0 * AVG(Revenue), 2) AS purchase_rate_pct
FROM sessions
GROUP BY product_page_band
ORDER BY MIN(ProductRelated);

-- Inspect seasonality and visitor mix before interpreting the overall gap.
SELECT Month,
       VisitorType,
       COUNT(*) AS sessions,
       SUM(Revenue) AS purchasing_sessions,
       ROUND(100.0 * AVG(Revenue), 2) AS purchase_rate_pct
FROM sessions
WHERE VisitorType IN ('New_Visitor', 'Returning_Visitor')
GROUP BY Month, VisitorType
ORDER BY Month, VisitorType;

-- Compare visitor types on the same month distribution.
-- Weights are pooled new/returning sessions in eligible months, excluding Other.
WITH monthly AS (
    SELECT Month,
           SUM(CASE WHEN VisitorType = 'New_Visitor' THEN 1 ELSE 0 END) AS new_sessions,
           SUM(CASE WHEN VisitorType = 'New_Visitor' THEN Revenue ELSE 0 END) AS new_purchases,
           SUM(CASE WHEN VisitorType = 'Returning_Visitor' THEN 1 ELSE 0 END) AS returning_sessions,
           SUM(CASE WHEN VisitorType = 'Returning_Visitor' THEN Revenue ELSE 0 END) AS returning_purchases
    FROM sessions
    WHERE VisitorType IN ('New_Visitor', 'Returning_Visitor')
    GROUP BY Month
), eligible AS (
    SELECT *, new_sessions + returning_sessions AS pooled_sessions
    FROM monthly
    WHERE new_sessions >= 30 AND returning_sessions > 0
)
SELECT COUNT(*) AS eligible_months,
       SUM(pooled_sessions) AS pooled_sessions,
       ROUND(100.0 * SUM(pooled_sessions * 1.0 * new_purchases / new_sessions)
             / SUM(pooled_sessions), 2) AS standardized_new_rate_pct,
       ROUND(100.0 * SUM(pooled_sessions * 1.0 * returning_purchases / returning_sessions)
             / SUM(pooled_sessions), 2) AS standardized_returning_rate_pct
FROM eligible;

-- Check whether the weekend pattern differs by visitor type.
SELECT VisitorType,
       Weekend,
       COUNT(*) AS sessions,
       SUM(Revenue) AS purchasing_sessions,
       ROUND(100.0 * AVG(Revenue), 2) AS purchase_rate_pct
FROM sessions
WHERE VisitorType IN ('New_Visitor', 'Returning_Visitor')
GROUP BY VisitorType, Weekend
ORDER BY VisitorType, Weekend;

-- Standardize new and returning purchase rates to the same mix of traffic categories.
-- Include only categories with at least 30 sessions in each visitor group.
WITH traffic_strata AS (
    SELECT TrafficType,
           SUM(CASE WHEN VisitorType = 'New_Visitor' THEN 1 ELSE 0 END) AS new_sessions,
           SUM(CASE WHEN VisitorType = 'New_Visitor' THEN Revenue ELSE 0 END) AS new_purchases,
           SUM(CASE WHEN VisitorType = 'Returning_Visitor' THEN 1 ELSE 0 END) AS returning_sessions,
           SUM(CASE WHEN VisitorType = 'Returning_Visitor' THEN Revenue ELSE 0 END) AS returning_purchases
    FROM sessions
    WHERE VisitorType IN ('New_Visitor', 'Returning_Visitor')
    GROUP BY TrafficType
), eligible AS (
    SELECT *
    FROM traffic_strata
    WHERE new_sessions >= 30 AND returning_sessions >= 30
)
SELECT COUNT(*) AS eligible_traffic_categories,
       SUM(new_sessions + returning_sessions) AS pooled_sessions,
       ROUND(100.0 * SUM((new_sessions + returning_sessions) * (1.0 * new_purchases / new_sessions))
             / SUM(new_sessions + returning_sessions), 2) AS standardized_new_rate_pct,
       ROUND(100.0 * SUM((new_sessions + returning_sessions) * (1.0 * returning_purchases / returning_sessions))
             / SUM(new_sessions + returning_sessions), 2) AS standardized_returning_rate_pct
FROM eligible;
