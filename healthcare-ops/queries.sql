-- Load data/members.csv as members and data/events.csv as events in SQLite.
-- One row in members is one synthetic enrollment; one row in events is one
-- completed/observed operational event. Dates are ISO YYYY-MM-DD.

-- Monthly enrollment volume.
SELECT strftime('%Y-%m', enrollment_date) AS cohort_month,
       COUNT(*) AS enrolled_members
FROM members
GROUP BY cohort_month
ORDER BY cohort_month;

-- Cohort-matured operational scorecard by enrollment channel.
-- The cutoff prevents recent members from being counted as failures before
-- they have had the full follow-up window to complete the measure.
WITH event_dates AS (
    SELECT member_id,
           MIN(CASE WHEN event_type = 'coach_contact_completed' THEN event_date END) AS first_contact_date,
           MIN(CASE WHEN event_type = 'day30_checkin_completed' THEN event_date END) AS day30_date,
           MIN(CASE WHEN event_type = 'day60_activity_observed' THEN event_date END) AS day60_date
    FROM events
    GROUP BY member_id
), member_dates AS (
    SELECT m.member_id,
           m.channel,
           m.enrollment_date,
           julianday(e.first_contact_date) - julianday(m.enrollment_date) AS contact_day,
           julianday(e.day30_date) - julianday(m.enrollment_date) AS day30_offset,
           julianday(e.day60_date) - julianday(m.enrollment_date) AS day60_offset
    FROM members AS m
    LEFT JOIN event_dates AS e ON e.member_id = m.member_id
)
SELECT channel,
       SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-7 days') THEN 1 ELSE 0 END) AS activation_eligible,
       SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-7 days')
                 AND contact_day BETWEEN 0 AND 7 THEN 1 ELSE 0 END) AS activation_completed,
       ROUND(100.0 * SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-7 days')
                 AND contact_day BETWEEN 0 AND 7 THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-7 days') THEN 1 ELSE 0 END), 0), 1) AS activation_rate_pct,
       SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-37 days') THEN 1 ELSE 0 END) AS day30_eligible,
       SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-37 days')
                 AND day30_offset BETWEEN 28 AND 37 THEN 1 ELSE 0 END) AS day30_completed,
       ROUND(100.0 * SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-37 days')
                 AND day30_offset BETWEEN 28 AND 37 THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-37 days') THEN 1 ELSE 0 END), 0), 1) AS day30_rate_pct,
       SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-74 days') THEN 1 ELSE 0 END) AS day60_eligible,
       SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-74 days')
                 AND day60_offset BETWEEN 60 AND 74 THEN 1 ELSE 0 END) AS day60_completed,
       ROUND(100.0 * SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-74 days')
                 AND day60_offset BETWEEN 60 AND 74 THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN date(enrollment_date) <= date('2026-09-30', '-74 days') THEN 1 ELSE 0 END), 0), 1) AS day60_rate_pct
FROM member_dates
GROUP BY channel
ORDER BY channel;

-- Basic reliability checks. Each result should be zero for the generated files.
SELECT (SELECT COUNT(*) FROM (SELECT member_id FROM members GROUP BY member_id HAVING COUNT(*) > 1)) AS duplicate_member_ids,
       (SELECT COUNT(*) FROM (SELECT event_id FROM events GROUP BY event_id HAVING COUNT(*) > 1)) AS duplicate_event_ids,
       (SELECT COUNT(*) FROM events AS e LEFT JOIN members AS m ON m.member_id = e.member_id WHERE m.member_id IS NULL) AS orphan_events,
       (SELECT COUNT(*) FROM events AS e JOIN members AS m ON m.member_id = e.member_id WHERE date(e.event_date) < date(m.enrollment_date)) AS events_before_enrollment,
       (SELECT COUNT(*) FROM events WHERE date(event_date) > date('2026-09-30')) AS events_after_snapshot;
