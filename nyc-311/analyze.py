"""Reproduce NYC 311 service-request metrics with Python's standard library."""
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median

default_path = Path(__file__).parent / "data" / "requests_2026_06_01_to_07.csv"
path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
records = list(csv.DictReader(path.open(newline="", encoding="utf-8-sig")))
if path == default_path:
    assert len(records) == 80941
assert len({r["unique_key"] for r in records}) == len(records)

counts = Counter()
hours = defaultdict(list)
closed = Counter()
missing_close = 0
negative_duration = 0
for r in records:
    kind = r["complaint_type"]
    counts[kind] += 1
    if not r["closed_date"]:
        missing_close += 1
        continue
    closed[kind] += 1
    start = datetime.fromisoformat(r["created_date"])
    end = datetime.fromisoformat(r["closed_date"])
    elapsed = (end - start).total_seconds() / 3600
    if elapsed < 0:
        negative_duration += 1
    else:
        hours[kind].append(elapsed)

print("Requests:", len(records))
print("Missing close date:", missing_close)
print("Negative duration excluded from medians:", negative_duration)
def percentile(values, fraction):
    ordered = sorted(values)
    pos = (len(ordered) - 1) * fraction
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)

for kind, n in counts.most_common(10):
    print(kind, "requests=", n, "closed_date_present=", closed[kind],
          "close_date_rate=", round(100 * closed[kind] / n, 2),
          "median_closure_hours=", round(median(hours[kind]), 2) if hours[kind] else "N/A",
          "p90_closure_hours=", round(percentile(hours[kind], .9), 2) if hours[kind] else "N/A")

if not records or "descriptor" not in records[0]:
    print(
        "Pothole-specific closure time: NOT CALCULATED; this seven-column extract omits "
        "descriptor, so Pothole requests cannot be separated from broader Street Condition requests."
    )
else:
    potholes = [
        r for r in records
        if r["complaint_type"] == "Street Condition"
        and r["descriptor"].strip().casefold() == "pothole"
    ]
    pothole_hours = []
    pothole_closed = 0
    pothole_negative = 0
    for r in potholes:
        if not r["closed_date"]:
            continue
        pothole_closed += 1
        elapsed = (
            datetime.fromisoformat(r["closed_date"])
            - datetime.fromisoformat(r["created_date"])
        ).total_seconds() / 3600
        if elapsed < 0:
            pothole_negative += 1
        else:
            pothole_hours.append(elapsed)
    print("Pothole requests:", len(potholes))
    print("Pothole close-date coverage:", round(100 * pothole_closed / len(potholes), 2) if potholes else "N/A", "%")
    print("Pothole negative durations excluded:", pothole_negative)
    print("Pothole valid closed requests:", len(pothole_hours))
    print("Pothole average closure hours:", round(mean(pothole_hours), 2) if pothole_hours else "N/A")
    print("Pothole median closure hours:", round(median(pothole_hours), 2) if pothole_hours else "N/A")
    print("Pothole 90th-percentile closure hours:", round(percentile(pothole_hours, .9), 2) if pothole_hours else "N/A")
