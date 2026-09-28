"""Reproduce NYC 311 service-request metrics with Python's standard library."""
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median

path = Path(__file__).parent / "data" / "requests_2026_06_01_to_07.csv"
records = list(csv.DictReader(path.open(newline="", encoding="utf-8-sig")))
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
for kind, n in counts.most_common(10):
    print(kind, "requests=", n, "closed_date_present=", closed[kind],
          "median_closure_hours=", round(median(hours[kind]), 2) if hours[kind] else "N/A")
