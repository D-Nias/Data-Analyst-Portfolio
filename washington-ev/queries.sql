-- Import the public CSV as table vehicles in SQLite.
-- Quoted names preserve the source column labels.

SELECT COUNT(*) AS washington_vehicles,
       COUNT(DISTINCT "DOL Vehicle ID") AS distinct_vehicle_ids
FROM vehicles
WHERE State = 'WA';

SELECT "Electric Vehicle Type" AS vehicle_type,
       COUNT(*) AS vehicles,
       ROUND(100.0 * COUNT(*) /
         (SELECT COUNT(*) FROM vehicles WHERE State = 'WA'), 2) AS share_pct
FROM vehicles
WHERE State = 'WA'
GROUP BY "Electric Vehicle Type"
ORDER BY vehicles DESC;

SELECT County,
       COUNT(*) AS registered_evs,
       SUM(CASE WHEN "Electric Vehicle Type" = 'Battery Electric Vehicle (BEV)'
           THEN 1 ELSE 0 END) AS battery_electric,
       ROUND(100.0 * SUM(CASE WHEN "Electric Vehicle Type" = 'Battery Electric Vehicle (BEV)'
           THEN 1 ELSE 0 END) / COUNT(*), 2) AS bev_share_pct
FROM vehicles
WHERE State = 'WA'
GROUP BY County
ORDER BY registered_evs DESC
LIMIT 10;
