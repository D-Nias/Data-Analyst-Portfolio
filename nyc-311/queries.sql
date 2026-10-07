-- Import the CSV as table requests in SQLite. Timestamps use ISO text.
-- Each row is one service request, identified by unique_key.

SELECT COUNT(*) AS requests,
       COUNT(DISTINCT unique_key) AS unique_requests,
       SUM(CASE WHEN closed_date IS NULL OR closed_date = '' THEN 1 ELSE 0 END) AS missing_close_date
FROM requests;

SELECT complaint_type,
       COUNT(*) AS request_count,
       SUM(CASE WHEN closed_date IS NOT NULL AND closed_date <> '' THEN 1 ELSE 0 END) AS close_date_present
FROM requests
GROUP BY complaint_type
ORDER BY request_count DESC
LIMIT 10;

-- This query computes closure hours per record. Use a median-capable SQL engine
-- or analyze.py for group medians; SQLite does not provide MEDIAN by default.
SELECT unique_key, complaint_type,
       ROUND((julianday(closed_date) - julianday(created_date)) * 24, 2) AS closure_hours
FROM requests
WHERE closed_date IS NOT NULL AND closed_date <> ''
  AND julianday(closed_date) >= julianday(created_date);

-- Import potholes_2026_06_01_to_07_retrieved_2026_10_07.csv as potholes.
-- This subset was filtered to Street Condition / Pothole in the source API.
SELECT COUNT(*) AS pothole_requests,
       SUM(CASE WHEN closed_date IS NOT NULL AND closed_date <> '' THEN 1 ELSE 0 END) AS close_date_present,
       ROUND(100.0 * SUM(CASE WHEN closed_date IS NOT NULL AND closed_date <> '' THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS close_date_coverage_pct,
       AVG(CASE WHEN closed_date IS NOT NULL AND closed_date <> ''
                     AND julianday(closed_date) >= julianday(created_date)
                THEN (julianday(closed_date) - julianday(created_date)) * 24 END) AS mean_valid_closure_hours
FROM potholes;

-- The Python analysis additionally calculates the median and 90th percentile.
SELECT unique_key,
       ROUND((julianday(closed_date) - julianday(created_date)) * 24, 2) AS closure_hours
FROM potholes
WHERE closed_date IS NOT NULL AND closed_date <> ''
  AND julianday(closed_date) >= julianday(created_date);
