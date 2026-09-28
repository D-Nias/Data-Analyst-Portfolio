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
