# NYC 311 service-request operations

![Bar charts showing the highest-volume request types and median recorded closure times](chart.svg)

## Executive brief

**Decision question:** Which request categories dominate incoming volume, and where do long closure tails warrant an operations review?

**Finding:** **Illegal Parking** generated **13,694** requests in the June 1–7, 2026 cohort, or **16.92%** of all **80,941** requests. Its median recorded time to close was **1.64 hours**, while **Damaged Tree** had a **47.77-hour** median and **Unsanitary Condition** had a **174.38-hour** median among requests with valid close times. These are fundamentally different workflows, so the differences are leads for investigation, not a performance ranking.

**Recommended next action:** Review intake staffing for high-volume, short-cycle types; inspect handoffs and field scheduling for long-cycle types. For an actual performance scorecard, report **volume, share with a close date, median, and 90th percentile together** within each complaint type.

## Cohort and KPI definitions

The [NYC Open Data 311 dataset](https://data.cityofnewyork.us/d/erm2-nwe9) was filtered to requests **created June 1–7, 2026**. One row represents one service request; all **80,941 unique keys** in the extract are distinct. Recorded closure hours equal `closed_date − created_date`. The **median** is the middle valid closed request; the **90th percentile** shows the long tail. Close-date coverage is requests with a close timestamp ÷ all requests of that type.

| Complaint type | Requests | Close-date coverage | Median hours | 90th-percentile hours |
| --- | ---: | ---: | ---: | ---: |
| Illegal Parking | 13,694 | 100.00% | 1.64 | 7.93 |
| Noise – Residential | 8,141 | 100.00% | 1.27 | 6.07 |
| Damaged Tree | 2,766 | 83.98% | 47.77 | 358.05 |
| Unsanitary Condition | 2,630 | 97.83% | 174.38 | 585.45 |

The long tail matters: for Damaged Tree, the 90th percentile among valid closed cases is about **15 days**. A median alone would conceal that spread. Its **83.98% close-date coverage** also means the displayed duration excludes many requests without a close timestamp.

## Quality and interpretation checks

- **3,649** requests have no close date. **14** have a close timestamp before the creation timestamp; those 14 are excluded from duration summaries.
- `closed_date` is an administrative system event. It is not proof of physical repair or resident satisfaction.
- Open requests are missing from the duration percentiles. This can make slower categories look faster, so coverage appears beside duration.
- This is one week, not an annual average. NYC updates the source daily, and fields can change after extraction.
- Borough comparisons require controlling for complaint mix and agency workflow before drawing performance conclusions.

## Reproduce

Run `python analyze.py` in this folder; it uses only Python's standard library and the included [seven-column extract](data/requests_2026_06_01_to_07.csv). `queries.sql` provides SQLite checks. The extract omits addresses and other location details. It came from the NYC Socrata API with this creation-date filter:

```text
created_date >= '2026-06-01T00:00:00' and created_date < '2026-06-08T00:00:00'
```

The [case-study page](index.html) gives a visual overview. **Source:** NYC Open Data, *311 Service Requests from 2020 to Present*, accessed September 28, 2026. This is a public-data practice analysis, not client or employer work.
