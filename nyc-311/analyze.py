"""Reproduce NYC 311 service-request metrics with the Python standard library."""
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).parent
DEFAULT_PATH = ROOT / "data" / "requests_2026_06_01_to_07.csv"
path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
if not path.exists():
    raise SystemExit(f"CSV not found: {path}")

with path.open(newline="", encoding="utf-8-sig") as source:
    reader = csv.DictReader(source)
    required = {"unique_key", "created_date", "closed_date", "complaint_type"}
    missing_columns = required - set(reader.fieldnames or [])
    if missing_columns:
        raise SystemExit(f"CSV is missing required columns: {', '.join(sorted(missing_columns))}")
    has_descriptor = "descriptor" in (reader.fieldnames or [])
    records = list(reader)

if not records:
    raise SystemExit("CSV contains no records")
if path == DEFAULT_PATH and len(records) != 80941:
    raise SystemExit(f"Expected 80,941 records in the included cohort extract, found {len(records)}")

keys = [row["unique_key"].strip() for row in records]
missing_keys = sum(not key for key in keys)
duplicate_keys = len([key for key in keys if key]) - len({key for key in keys if key})
if missing_keys or duplicate_keys:
    raise SystemExit(f"Request key check failed: missing={missing_keys}, duplicate rows={duplicate_keys}")


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def duration_hours(row):
    start = datetime.fromisoformat(row["created_date"])
    end = datetime.fromisoformat(row["closed_date"])
    return (end - start).total_seconds() / 3600


def describe(values):
    return {
        "valid_closed_requests": len(values),
        "mean_hours": round(mean(values), 2) if values else None,
        "median_hours": round(median(values), 2) if values else None,
        "p90_hours": round(percentile(values, 0.9), 2) if values else None,
    }


counts = Counter()
closed = Counter()
negative_by_type = Counter()
hours = defaultdict(list)
missing_close = 0
negative_duration = 0
for row in records:
    kind = row["complaint_type"].strip()
    counts[kind] += 1
    if not row["closed_date"].strip():
        missing_close += 1
        continue
    closed[kind] += 1
    elapsed = duration_hours(row)
    if elapsed < 0:
        negative_duration += 1
        negative_by_type[kind] += 1
    else:
        hours[kind].append(elapsed)

category_metrics = []
for kind, count in counts.most_common(10):
    coverage = round(100 * closed[kind] / count, 2) if count else None
    measures = describe(hours[kind])
    category_metrics.append({
        "complaint_type": kind,
        "requests": count,
        "close_date_present": closed[kind],
        "close_date_coverage_pct": coverage,
        "negative_durations_excluded": negative_by_type[kind],
        **measures,
    })

summary = {
    "dataset": "NYC 311 Service Requests from 2020 to Present",
    "created_date_start": "2026-06-01T00:00:00",
    "created_date_end_exclusive": "2026-06-08T00:00:00",
    "request_count": len(records),
    "unique_request_keys": len(set(keys)),
    "quality": {
        "missing_keys": missing_keys,
        "duplicate_key_rows": duplicate_keys,
        "missing_close_dates": missing_close,
        "negative_durations_excluded": negative_duration,
    },
    "top_complaint_types": category_metrics,
}

print("Requests:", len(records))
print("Missing close date:", missing_close)
print("Negative duration excluded:", negative_duration)
for result in category_metrics:
    print(
        result["complaint_type"],
        "requests=", result["requests"],
        "close_date_coverage=", result["close_date_coverage_pct"], "%",
        "mean_hours=", result["mean_hours"],
        "median_hours=", result["median_hours"],
        "p90_hours=", result["p90_hours"],
    )

if has_descriptor:
    potholes = [
        row for row in records
        if row["complaint_type"].strip() == "Street Condition"
        and row["descriptor"].strip().casefold() == "pothole"
    ]
    pothole_missing_close = sum(not row["closed_date"].strip() for row in potholes)
    pothole_closed = [row for row in potholes if row["closed_date"].strip()]
    pothole_durations = []
    pothole_negative = 0
    for row in pothole_closed:
        elapsed = duration_hours(row)
        if elapsed < 0:
            pothole_negative += 1
        else:
            pothole_durations.append(elapsed)
    pothole_summary = {
        "source_file": path.name,
        "filters": {
            "created_date_start": "2026-06-01T00:00:00",
            "created_date_end_exclusive": "2026-06-08T00:00:00",
            "complaint_type": "Street Condition",
            "descriptor": "Pothole",
        },
        "request_count": len(potholes),
        "closed_date_present": len(pothole_closed),
        "close_date_coverage_pct": round(100 * len(pothole_closed) / len(potholes), 2) if potholes else None,
        "missing_close_dates": pothole_missing_close,
        "negative_durations_excluded": pothole_negative,
        "closure_time": describe(pothole_durations),
        "interpretation": "Close timestamp is an administrative record and does not establish physical repair.",
    }
    (ROOT / "pothole_summary.json").write_text(json.dumps(pothole_summary, indent=2) + "\n", encoding="utf-8")
    print("Pothole requests:", len(potholes))
    print("Pothole close-date coverage:", pothole_summary["close_date_coverage_pct"], "%")
    print("Pothole valid closed requests:", len(pothole_durations))
    print("Pothole average closure hours:", pothole_summary["closure_time"]["mean_hours"])
    print("Pothole median closure hours:", pothole_summary["closure_time"]["median_hours"])
    print("Pothole 90th-percentile closure hours:", pothole_summary["closure_time"]["p90_hours"])

if path == DEFAULT_PATH:
    (ROOT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
