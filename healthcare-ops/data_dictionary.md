# Data dictionary

All rows are generated and fictional. The fixed random seed is in `generate_data.py`.

## `members.csv`

| Field | Type | Meaning |
| --- | --- | --- |
| `member_id` | Text | Synthetic unique enrollment key (`SYN` prefix). Not a real person identifier. |
| `enrollment_date` | ISO date | Fictional program enrollment date. |
| `channel` | Category | Simulated enrollment channel: `Direct` or `Employer`. |
| `care_team` | Category | Fictional assigned team ID. No person names are included. |

**Grain:** one row per synthetic enrollment.

## `events.csv`

| Field | Type | Meaning |
| --- | --- | --- |
| `event_id` | Text | Synthetic unique event key. |
| `member_id` | Text | Synthetic foreign key to `members.member_id`. |
| `event_type` | Category | `coach_contact_completed`, `day30_checkin_completed`, or `day60_activity_observed`. |
| `event_date` | ISO date | Fictional date of the completed/observed touchpoint. |

**Grain:** one row per synthetic touchpoint event. Missing events are not stored as rows; KPI denominators come from the eligible member cohort.

## Snapshot and timing rules

The scorecard is fixed at `2026-09-30`. A member is eligible for a metric only when the full window's last day has passed by the snapshot. A milestone counts only when its event falls inside the explicitly defined day window. This prevents right-censored recent enrollments from being counted as failures.
